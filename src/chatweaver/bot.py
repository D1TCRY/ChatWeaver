from __future__ import annotations

import base64
import pathlib
import time
from typing import Any, Optional

from openai.types import FileObject

from .model import Model
from .data import ChatWeaverSystemRules
from .schema import Schema
from .helpers import is_valid_url, is_valid_path, is_file_id
from .bot_completion_result import BotCompletionResult
from .metadata_container import MetadataContainer


class Bot(object):
    """
    A conversational bot that uses a provided Model instance.
    The bot can be frozen and later restored without requiring a valid API key at construction time.
    """

    def __init__(
        self,
        model: Optional[Model] = None,
        rules: Optional[str] = ChatWeaverSystemRules.default(),
        name: str = "AI Bot",
        schema: Optional[Schema] = None,
        time_format: str = "%d/%m/%Y %H:%M:%S",
        **kwargs,
    ) -> None:
        """
        A conversational bot that uses a provided Model instance.
        The bot can be frozen and later restored without requiring a valid API key at construction time.
        """

        self.__default_attributes: dict[str, Any] = {
            "name": "AI Bot",
            "rules": ChatWeaverSystemRules.default(),
            "time_format": "%d/%m/%Y %H:%M:%S",
        }

        # Restore from snapshot
        if "define" in kwargs:
            attributes: dict[str, dict[str, Any]] = kwargs["define"]
            props: dict[str, Any] = attributes.get("properties", {})
            extra: dict[str, Any] = attributes.get("extra", {})

            for k, v in props.items():
                setattr(self, k, v)
            for k, v in extra.items():
                setattr(self, k, v)

            if getattr(self, "_Bot__model", None) is None:
                raise ValueError("<Invalid snapshot: missing 'model'>")

            return

        # Normal init
        self.time_format = time_format
        self.name = name
        self.rules = rules
        self.schema = schema
        self.model = model if model is not None else Model(api_key=None)


    # -------- FREEZE / THAW --------
    def freeze(self, include_secrets: bool = False) -> dict[str, Any]:
        """
        Return a serializable snapshot of the bot.
        Secrets are excluded by default.
        """
        schema_snapshot: Optional[dict[str, Any]] = None
        if self.schema is not None:
            schema_snapshot = self.schema.freeze()

        return {
            "version": 1,
            "properties": {
                "name": self.name,
                "rules": self.__input_rules,          # store raw input rules (without name suffix)
                "time_format": self.time_format,
                "schema": schema_snapshot,            # snapshot or None
                "model": self.model.freeze(include_secrets=include_secrets),
            },
            "extra": {}
        }

    @classmethod
    def thaw(
        cls,
        snapshot: dict[str, Any],
        model: Optional[Model] = None,
        api_key: Optional[str] = None,
    ) -> "Bot":
        """
        Restore a Bot from a snapshot.

        If a Model instance is provided, it will be used.
        If api_key is provided, it overrides the Model api_key during restoration.
        """
        if not isinstance(snapshot, dict):
            raise TypeError("<Invalid snapshot: expected dict>")

        props = snapshot.get("properties", {})
        if not isinstance(props, dict):
            raise ValueError("<Invalid snapshot: missing properties dict>")

        # Restore / select Model
        model_snapshot = props.get("model")
        if model is None:
            if not isinstance(model_snapshot, dict):
                raise ValueError("<Invalid snapshot: missing model snapshot>")
            model = Model.thaw(model_snapshot, api_key=api_key)
        else:
            if api_key is not None:
                model.api_key = api_key

        # Restore schema (if present)
        schema_snapshot = props.get("schema")
        schema_obj: Optional[Schema]
        if schema_snapshot is None:
            schema_obj = None
        else:
            if not isinstance(schema_snapshot, dict):
                raise ValueError("<Invalid snapshot: schema must be a dict snapshot or None>")
            schema_obj = Schema.thaw(schema_snapshot)

        define = {
            "properties": {
                "name": props.get("name", "AI Bot"),
                "rules": props.get("rules", ChatWeaverSystemRules.default()),
                "time_format": props.get("time_format", "%d/%m/%Y %H:%M:%S"),
                "schema": schema_obj,
                "model": model,
            },
            "extra": snapshot.get("extra", {}),
        }

        return cls(define=define)

    # -------- MAGIC METHODS --------
    def __str__(self) -> str:
        return f"<{self.__class__.__name__} | name: {self.__name}, api_key: {self.model.api_key_hint()!r}>"

    def __repr__(self) -> str:
        is_name: bool = self.name == self.__default_attributes["name"]
        is_rules: bool = self.__input_rules == self.__default_attributes["rules"]
        is_time: bool = self.time_format == self.__default_attributes["time_format"]

        parts: list[str] = []
        if not is_name:
            parts.append(f"name={self.name!r}")
        if not is_rules:
            parts.append(f"rules={self.__input_rules!r}")
        if not is_time:
            parts.append(f"time_format={self.time_format!r}")

        parts.append(f"model={self.model!r}")

        if self.schema is not None:
            parts.append(f"schema={self.schema!r}")

        return f"Bot({', '.join(parts)})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Bot):
            return False

        same_name = self.name == other.name
        same_rules = self.__input_rules == other.__input_rules
        same_time = self.time_format == other.time_format
        same_model = self.model == other.model
        same_schema = self.schema == other.schema

        return same_name and same_rules and same_time and same_model and same_schema

    # -------- PROPERTIES --------
    @property
    def model(self) -> Model:
        """Return the Model instance used by the bot."""
        return self.__model
    @model.setter
    def model(self, new: Model) -> None:
        """Set the Model instance used by the bot."""
        if not isinstance(new, Model):
            raise TypeError(f"<Invalid 'model' type: Expected Model, got {type(new)}>")

        self.__model = new

    @property
    def rules(self) -> str:
        """Return the active rules string including the bot name."""
        return f"[Your name as AI is: '{self.name}']\n" + self.__rules
    @rules.setter
    def rules(self, new_rules: Optional[str]) -> None:
        """Set the base rules string for the bot."""
        self.__input_rules = str(new_rules) if new_rules is not None else ChatWeaverSystemRules.default()
        self.__rules = self.__input_rules

    @property
    def name(self) -> str:
        """Return the bot name."""
        return self.__name
    @name.setter
    def name(self, new_name: str) -> None:
        """Set the bot name."""
        new_name = str(new_name).strip()
        if len(new_name) == 0:
            raise ValueError("<Invalid 'name': cannot be empty>")
        self.__name = new_name

    @property
    def time_format(self) -> str:
        """Return the time format used by the bot."""
        return self.__time_format
    @time_format.setter
    def time_format(self, new_time_format: str) -> None:
        """Set and validate a time format string."""
        try:
            time.strftime(str(new_time_format), time.localtime(time.time()))
            self.__time_format = str(new_time_format)
        except Exception:
            raise ValueError("<Invalid 'time_format': expected a valid strftime format>")

    @property
    def schema(self) -> Optional[Schema]:
        """Return the default response schema."""
        return self.__schema
    @schema.setter
    def schema(self, new: Optional[Schema]) -> None:
        """Set the default response schema."""
        if not isinstance(new, (Schema, type(None))):
            raise TypeError("<Invalid 'schema' type: expected Schema or None>")
        self.__schema = new

    # -------- HELPERS --------
    def _ensure_remote_ready(self) -> None:
        """
        Ensure remote services are available.
        This does not prevent the bot from existing.
        """
        # Accessing client triggers lazy validation inside Model
        _ = self.model.client

    def get_metadata_messages(
        self,
        img_data: str | pathlib.Path | list[str | pathlib.Path] | None = None,
        file_data: str | pathlib.Path | FileObject | list[str | pathlib.Path | FileObject] | None = None,
    ) -> dict[str, list[dict[str, Any]]]:
        """
        Build metadata message blocks for images and files.
        """
        if not (
            (
                isinstance(img_data, list)
                and len(img_data) > 0
                and all(isinstance(item, (str, pathlib.Path)) for item in img_data)
            )
            or isinstance(img_data, (str, pathlib.Path))
            or img_data is None
        ):
            raise TypeError("<img_data must be a string, pathlib.Path, or list of strings/paths>")

        if not (
            (
                isinstance(file_data, list)
                and len(file_data) > 0
                and all(isinstance(item, (str, pathlib.Path, FileObject)) for item in file_data)
            )
            or isinstance(file_data, (str, pathlib.Path, FileObject))
            or file_data is None
        ):
            raise TypeError("<file_data must be a string, pathlib.Path, FileObject, or list of them>")

        image_messages: list[dict[str, Any]] = []
        file_messages: list[dict[str, Any]] = []
        images_content: list[Any] = []
        files_content: list[Any] = []

        # ---- images ----
        if img_data is not None:
            img_list = [img_data] if isinstance(img_data, (str, pathlib.Path)) else img_data

            for i, image in enumerate(img_list):
                if is_valid_url(image):
                    img_list[i] = str(image)
                elif is_valid_path(image):
                    img_list[i] = (
                        "data:image/png;base64,"
                        + base64.b64encode(open(image, "rb").read()).decode("utf-8")
                    )
                else:
                    raise ValueError(f"<Invalid image path or url: {image}>")

            for image in img_list:
                image_messages.append({"type": "image_url", "image_url": {"url": image}})
                images_content.append(image)

        # ---- files ----
        if file_data is not None:
            file_list = [file_data] if isinstance(file_data, (str, pathlib.Path, FileObject)) else file_data

            for f in file_list:
                # 1) already a file_id
                if is_file_id(f):
                    uploaded_id = str(f)

                # 2) local path -> upload (requires remote services)
                elif is_valid_path(f):
                    self._ensure_remote_ready()
                    with open(f, "rb") as fh:
                        uploaded = self.model.client.files.create(
                            file=fh,
                            purpose="user_data",
                        )
                    files_content.append(f)
                    uploaded_id = uploaded.id

                # 3) URL not supported
                elif isinstance(f, str) and is_valid_url(f):
                    raise ValueError(f"<Invalid file source (URL not supported): {f}>")

                else:
                    raise ValueError(f"<Invalid file path or file_id: {f}>")

                file_messages.append({"type": "file", "file": {"file_id": uploaded_id}})

        return {
            "image_messages": image_messages,
            "file_messages": file_messages,
            "images_content": images_content,
            "files_content": files_content,
        }

    # -------- ACTIONS --------
    def completion(
        self,
        prompt: str,
        user: str = "User",
        history: list | None = None,
        img_data: str | pathlib.Path | list[str | pathlib.Path] | None = None,
        file_data: str | pathlib.Path | FileObject | list[str | pathlib.Path | FileObject] | None = None,
        response_schema: Schema | None = None,
    ) -> BotCompletionResult:
        """
        Create a chat completion using the configured model and bot settings.
        """
        start_date = time.strftime(self.time_format, time.localtime(time.time()))
        prompt = str(prompt)

        messages: list[dict[str, Any | list]] = [
            {"role": "system", "content": self.rules + f"\n[The name of the user is: '{user}']"},
            {"role": "user", "content": [{"type": "text", "text": prompt}]},
        ]

        if history is not None:
            messages = [dict(message) for message in history] + messages

        metadata_messages = self.get_metadata_messages(img_data=img_data, file_data=file_data)

        for image_message in metadata_messages["image_messages"]:
            messages[1]["content"].append(image_message)

        for file_message in metadata_messages["file_messages"]:
            messages[1]["content"].append(file_message)

        if not isinstance(response_schema, (Schema, type(None))):
            raise TypeError("<'response_schema' must be Schema or None>")

        if response_schema is None:
            response_schema = self.schema

        self._ensure_remote_ready()

        start = time.perf_counter()
        response = self.model.client.chat.completions.create(
            model=self.model.model,
            messages=messages,  # type: ignore
            response_format=response_schema.resolve() if response_schema else None,  # type: ignore
        )
        end = time.perf_counter()

        final_date = time.strftime(self.time_format, time.localtime(time.time()))

        msg = response.choices[0].message
        content = msg.content if msg.content is not None else msg.refusal

        return BotCompletionResult(
            content=content,
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
            total_tokens=response.usage.total_tokens,
            start_date=start_date,
            delta_time=end - start,
            final_date=final_date,
            input_metadata=MetadataContainer(
                images=metadata_messages["images_content"],
                files=metadata_messages["files_content"],
            ),
            output_metadata=MetadataContainer(images=[], files=[]),
        )

    def __generation(
        self,
        prompt: str,
        user: str = "User",
        history: list | None = None,
        img_data: str | pathlib.Path | list[str | pathlib.Path] | None = None,
        file_data: str | pathlib.Path | FileObject | list[str | pathlib.Path | FileObject] | None = None,
        response_schema: Schema | None = None,
    ) -> BotCompletionResult:
        """
        Placeholder for a generation-style API.
        """
        raise NotImplementedError
