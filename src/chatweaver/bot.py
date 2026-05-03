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
        max_completion_tokens: Optional[int] = None,
        auto_continue: bool = False,
        max_continuations: int = 0,
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
            "max_completion_tokens": None,
            "auto_continue": False,
            "max_continuations": 0,
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
        self.max_completion_tokens = max_completion_tokens
        self.auto_continue = auto_continue
        self.max_continuations = max_continuations
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
                "max_completion_tokens": self.max_completion_tokens,
                "auto_continue": self.auto_continue,
                "max_continuations": self.max_continuations,
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
                "max_completion_tokens": props.get("max_completion_tokens", None),
                "auto_continue": props.get("auto_continue", False),
                "max_continuations": props.get("max_continuations", 0),
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
        is_max_completion_tokens: bool = self.max_completion_tokens == self.__default_attributes["max_completion_tokens"]
        is_auto_continue: bool = self.auto_continue == self.__default_attributes["auto_continue"]
        is_max_continuations: bool = self.max_continuations == self.__default_attributes["max_continuations"]

        parts: list[str] = []
        if not is_name:
            parts.append(f"name={self.name!r}")
        if not is_rules:
            parts.append(f"rules={self.__input_rules!r}")
        if not is_time:
            parts.append(f"time_format={self.time_format!r}")
        if not is_max_completion_tokens:
            parts.append(f"max_completion_tokens={self.max_completion_tokens!r}")
        if not is_auto_continue:
            parts.append(f"auto_continue={self.auto_continue!r}")
        if not is_max_continuations:
            parts.append(f"max_continuations={self.max_continuations!r}")

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
        same_max_completion_tokens = self.max_completion_tokens == other.max_completion_tokens
        same_auto_continue = self.auto_continue == other.auto_continue
        same_max_continuations = self.max_continuations == other.max_continuations

        return (
            same_name
            and same_rules
            and same_time
            and same_model
            and same_schema
            and same_max_completion_tokens
            and same_auto_continue
            and same_max_continuations
        )

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

    @property
    def max_completion_tokens(self) -> Optional[int]:
        """
        Return the default upper bound for generated completion tokens.

        None means ChatWeaver does not send any output-token cap to OpenAI.
        The model/API can still stop earlier because of the model's own output
        limit, context window, safety behavior, or natural completion.
        """
        return self.__max_completion_tokens
    @max_completion_tokens.setter
    def max_completion_tokens(self, new: Optional[int]) -> None:
        """Set the default completion-token cap. None means no cap is sent."""
        if new is None:
            self.__max_completion_tokens = None
            return

        try:
            value = int(new)
        except Exception:
            raise TypeError("<Invalid 'max_completion_tokens': expected int or None>")

        if value <= 0:
            raise ValueError("<Invalid 'max_completion_tokens': must be > 0 or None>")

        self.__max_completion_tokens = value

    @property
    def auto_continue(self) -> bool:
        """Return whether the bot should continue automatically after length truncation."""
        return self.__auto_continue
    @auto_continue.setter
    def auto_continue(self, new: bool) -> None:
        """Enable or disable automatic continuation when finish_reason == 'length'."""
        if not isinstance(new, bool):
            raise TypeError("<Invalid 'auto_continue': expected bool>")
        self.__auto_continue = new

    @property
    def max_continuations(self) -> int:
        """Return how many follow-up continuation calls are allowed."""
        return self.__max_continuations
    @max_continuations.setter
    def max_continuations(self, new: int) -> None:
        """Set the maximum number of automatic continuation calls."""
        try:
            value = int(new)
        except Exception:
            raise TypeError("<Invalid 'max_continuations': expected int>")

        if value < 0:
            raise ValueError("<Invalid 'max_continuations': must be >= 0>")

        self.__max_continuations = value

    def _normalize_history(self, history: list) -> list[dict[str, Any]]:
        """
        Convert ChatWeaver TextNode/dict history into OpenAI-compatible messages.
        Extra ChatWeaver metadata such as owner, tokens, date, image_data, and
        file_data is intentionally not forwarded to the API.
        """
        normalized: list[dict[str, Any]] = []
        allowed_roles = {"system", "developer", "user", "assistant", "tool"}

        for item in history:
            message = dict(item)
            role = message.get("role")
            content = message.get("content")

            if role not in allowed_roles:
                raise ValueError(f"<Invalid history role: {role!r}>")

            if content is None:
                content = ""

            normalized.append({
                "role": role,
                "content": content,
            })

        return normalized

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
                if is_valid_url(image): # type: ignore
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
                    with open(f, "rb") as fh: # type: ignore
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
        max_completion_tokens: Optional[int] = None,
        auto_continue: Optional[bool] = None,
        max_continuations: Optional[int] = None,
    ) -> BotCompletionResult:
        """
        Generate a chat completion using the current bot configuration.

        The method builds the system/user messages, optionally includes previous
        history, images, files, and a response schema, then sends the request to
        the configured model.

        By default, `max_completion_tokens` is None, so ChatWeaver does not impose
        an output-token limit and lets the model use its available capacity.
        If `auto_continue` is enabled, the bot can request follow-up completions
        when the response is cut off because of token limits.

        Args:
            prompt: User prompt to send to the model.
            user: Name of the user shown in the system context.
            history: Optional previous messages to include in the request.
            img_data: Optional image path, URL, or list of images.
            file_data: Optional file path, file id/object, or list of files.
            response_schema: Optional schema for structured output.
            max_completion_tokens: Optional maximum number of output tokens.
            auto_continue: Whether to continue automatically if output is truncated.
            max_continuations: Maximum number of automatic continuations.

        Returns:
            A BotCompletionResult containing the response text, token usage,
            timing information, metadata, and completion status.
        """
        start_date = time.strftime(self.time_format, time.localtime(time.time()))
        prompt = str(prompt)

        user_message: dict[str, Any | list] = {
            "role": "user",
            "content": [{"type": "text", "text": prompt}],
        }

        messages: list[dict[str, Any | list]] = [
            {"role": "system", "content": self.rules + f"\n[The name of the user is: '{user}']"},
            user_message,
        ]

        if history is not None:
            messages = self._normalize_history(history) + messages

        metadata_messages = self.get_metadata_messages(img_data=img_data, file_data=file_data)

        for image_message in metadata_messages["image_messages"]:
            user_message["content"].append(image_message)  # type: ignore[union-attr]

        for file_message in metadata_messages["file_messages"]:
            user_message["content"].append(file_message)  # type: ignore[union-attr]

        if not isinstance(response_schema, (Schema, type(None))):
            raise TypeError("<'response_schema' must be Schema or None>")

        if response_schema is None:
            response_schema = self.schema

        effective_max_completion_tokens = (
            self.max_completion_tokens
            if max_completion_tokens is None
            else max_completion_tokens
        )
        if effective_max_completion_tokens is not None:
            try:
                effective_max_completion_tokens = int(effective_max_completion_tokens)
            except Exception:
                raise TypeError("<'max_completion_tokens' must be int or None>")
            if effective_max_completion_tokens <= 0:
                raise ValueError("<'max_completion_tokens' must be > 0 or None>")

        effective_auto_continue = self.auto_continue if auto_continue is None else bool(auto_continue)
        effective_max_continuations = (
            self.max_continuations
            if max_continuations is None
            else int(max_continuations)
        )

        if effective_max_continuations < 0:
            raise ValueError("<'max_continuations' must be >= 0>")

        if response_schema is not None and effective_auto_continue and effective_max_continuations > 0:
            raise ValueError("<'auto_continue' is not compatible with structured response_schema>")

        self._ensure_remote_ready()

        request_kwargs: dict[str, Any] = {
            "model": self.model.model,
            "messages": messages,
        }

        if response_schema is not None:
            request_kwargs["response_format"] = response_schema.resolve()

        if effective_max_completion_tokens is not None:
            request_kwargs["max_completion_tokens"] = effective_max_completion_tokens

        start = time.perf_counter()

        response = self.model.client.chat.completions.create(**request_kwargs)  # type: ignore[arg-type]
        choice = response.choices[0]
        msg = choice.message
        content = msg.content if msg.content is not None else (msg.refusal or "")

        all_content: list[str] = [str(content)]
        finish_reason = choice.finish_reason
        continuations_used = 0

        prompt_tokens = int(response.usage.prompt_tokens if response.usage else 0)
        completion_tokens = int(response.usage.completion_tokens if response.usage else 0)
        total_tokens = int(response.usage.total_tokens if response.usage else 0)

        while (
            effective_auto_continue
            and finish_reason == "length"
            and continuations_used < effective_max_continuations
        ):
            continuations_used += 1

            messages.append({"role": "assistant", "content": all_content[-1]})
            messages.append({
                "role": "user",
                "content": "Continue exactly where you stopped. Do not repeat previous text.",
            })
            request_kwargs["messages"] = messages

            response = self.model.client.chat.completions.create(**request_kwargs)  # type: ignore[arg-type]
            choice = response.choices[0]
            msg = choice.message
            next_content = msg.content if msg.content is not None else (msg.refusal or "")

            all_content.append(str(next_content))
            finish_reason = choice.finish_reason

            prompt_tokens += int(response.usage.prompt_tokens if response.usage else 0)
            completion_tokens += int(response.usage.completion_tokens if response.usage else 0)
            total_tokens += int(response.usage.total_tokens if response.usage else 0)

        end = time.perf_counter()
        final_date = time.strftime(self.time_format, time.localtime(time.time()))

        return BotCompletionResult(
            content="".join(all_content),
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            start_date=start_date,
            delta_time=end - start,
            final_date=final_date,
            input_metadata=MetadataContainer(
                images=metadata_messages["images_content"],
                files=metadata_messages["files_content"],
            ),
            output_metadata=MetadataContainer(images=[], files=[]),
            finish_reason=finish_reason,
            continuations=continuations_used,
        )

    def __generation(
        self,
        prompt: str,
        user: str = "User",
        history: list | None = None,
        img_data: str | pathlib.Path | list[str | pathlib.Path] | None = None,
        file_data: str | pathlib.Path | FileObject | list[str | pathlib.Path | FileObject] | None = None,
        response_schema: Schema | None = None,
        max_completion_tokens: Optional[int] = None,
        auto_continue: Optional[bool] = None,
        max_continuations: Optional[int] = None,
    ) -> BotCompletionResult:
        """
        Placeholder for a generation-style API.
        """
        raise NotImplementedError
