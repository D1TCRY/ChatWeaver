import pathlib
from typing import Any
import base64

import openai
from openai.types import FileObject

from .Model import Model
from .data import ChatWeaverSystemRules
from .Schema import Schema
from .helpers import is_valid_url, is_valid_path, is_file_id
from .BotGenerationResult import BotGenerationResult
from .MetadataContainer import MetadataContainer

import time



class Bot(Model):
    """
    # Bot

    ## Description
    Represents a conversational AI bot based on a specific model. This class allows customization of rules, bot name, and associated model behavior. It supports managing user prompts, handling responses, and integrating optional images or files.
    """

    def __init__(
            self,
            *args,
            rules: str | None = ChatWeaverSystemRules.default(),
            name: str = "AI Bot",
            schema: Schema | None = None,
            cw_model: Model | None = None,
            **kwargs
    ) -> None:
        """
            # Bot

            ## Description
            Represents a conversational AI bot based on a specific model. This class allows customization of rules,
            bot name, and associated model behavior. It supports managing user prompts, handling responses, and
            integrating optional images or files.

            ## Attributes
            ```python
            bot_rules: str         # The rules that define the bot's behavior and responses.
            bot_name: str          # The name of the bot (default is "AI Bot").
            bot_time_format: str   # The format used for time-related operations (default is "%d/%m/%Y %H:%M:%S").
            __rules: str           # Internal representation of the bot's rules.
            __name: str            # Internal representation of the bot's name.
            __time_format: str     # Internal format string for time-based functionalities.
            __model: Model         # The model instance associated with this bot.
            ```

            ## Methods
            ```python
            __init__(*args, rules, name, cw_model, **kwargs) -> None
                # Initializes the bot's attributes (rules, name, time format) and sets or creates the underlying Model.

            __str__() -> str
                # Returns a user-friendly string representation of the bot.

            __repr__() -> str
                # Returns a formal string representation of the bot, including its name, rules, and underlying Model info.

            __eq__(other: Bot) -> bool
                # Checks for equality by comparing the rules, name, and model of both Bot instances.

            bot_Model -> Model
                # Getter property that returns the underlying Model instance by calling super().

            bot_rules -> str
                # Getter property returning the bot's rules with the current bot name appended.

            bot_name -> str
                # Getter property returning the bot's name.

            bot_time_format -> str
                # Getter property returning the bot's internal time format.

            bot_rules.setter(new_rules: str | None) -> None
                # Setter property to update the bot's rules, falling back to a default if None is provided.

            bot_name.setter(new_name: str) -> None
                # Setter property to update the bot's name.

            bot_time_format.setter(new_time_format: str) -> None
                # Setter property to update the bot's time format, raising a ValueError if invalid.

            response(prompt, user, history, image_path, file_path) -> dict[str, Any]
                # Generates a response to a user's prompt, optionally including conversation history, images, or files.
            ```

            ---

            # __init__

            ## Description
            Initialize the Bot instance. This constructor sets default values for the bot's time format, name,
            and rules. It also manages an optional Model instance (cw_model). If no cw_model is provided,
            the constructor relies on the parent Model class to initialize the model.

            ## Parameters
            ```python
            *args: Any
                # Additional arguments passed to the superclass (Model) if no cw_model is provided.
            rules: str | None
                # The rules that define the bot's behavior; defaults to a standard rule set if None.
            name: str
                # The name of the bot; defaults to "AI Bot".
            cw_model: Model | None
                # An existing Model instance. If None, a new Model is created using *args and **kwargs.
            **kwargs: Any
                # Additional keyword arguments passed to the superclass (Model) if no cw_model is provided.
            ```

            ## Raises
            ```python
            TypeError
                # Raised if 'cw_model' is provided but is not an instance of Model.
            ```
        """

        # time format
        self.bot_time_format = "%d/%m/%Y %H:%M:%S"

        # name
        self.bot_name = str(name)

        # rules
        self.bot_rules = rules

        # schema
        self.bot_schema = schema

        # define super() [Model]
        if not isinstance(cw_model, Model) and cw_model is not None:
            raise TypeError(f"<Invalid 'cw_model' type: Expected 'Model' instance, got {type(cw_model)}>")
        if cw_model == None:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(model=cw_model.model_model, api_key=cw_model.model_api_key)

        # default attributes
        self.__default_attributes = {
            "name": "AI Bot",
            "rules": ChatWeaverSystemRules.default()
        }

    # -------- MAGIC METHODS --------
    def __str__(self) -> str:
        """
            # __str__

            ## Description
            Return a user-friendly string representation of the bot. By default, this includes the bot's name.
        """

        return f"<Bot | {self.__name}>"

    def __repr__(self) -> str:
        """
            # __repr__

            ## Description
            Return a formal string representation of the bot, useful for debugging or logging. This includes
            the bot name, any custom rules (if different from the default), and the representation of the
            associated Model instance.
        """

        is_name: bool = self.bot_name == self.__default_attributes["name"]
        is_rules: bool = self.bot_rules == self.__default_attributes["rules"]

        str_name: str = f"name={repr(self.bot_name)}," if not is_name else ""
        str_rules: str = f"rules={repr(self.bot_rules)}," if not is_rules else ""

        return f"Bot({str_name} {str_rules} cw_model={super().__repr__()})"

    def __eq__(self, other) -> bool:
        """
            # __eq__

            ## Description
            Compare this Bot instance to another Bot instance for equality. Two Bot instances are considered
            equal if they share the same rules, name, and underlying Model.

            ## Parameters
            ```python
            other: Bot
                # The Bot instance to compare with the current instance.
            ```

            ## Returns
            ```python
            bool
                # True if both Bot instances match in rules, name, and model; False otherwise.
            ```
        """

        if not isinstance(other, Bot):
            return False

        is_rules = self.bot_rules == other.bot_rules
        is_name = self.bot_name == other.bot_name

        is_model = eval(self.bot_Model.__repr__()) == eval(other.bot_Model.__repr__())

        return is_rules and is_name and is_model

    # -------- PROPERTY --------
    @property
    def bot_Model(self) -> Model:
        """
            # bot_Model (getter)

            ## Description
            Retrieve the underlying Model instance for this Bot by invoking the superclass directly.
            This method allows for model-based operations without exposing the internals of the Bot class.
        """

        return super()

    @property
    def bot_rules(self) -> str:
        """
            # bot_rules (getter)

            ## Description
            Retrieve the current rules used by the bot. The returned string automatically includes
            the bot's name for context in conversations.
        """

        return self.__rules + f" Your name is {self.bot_name}"

    @bot_rules.setter
    def bot_rules(self, new_rules: str | None) -> None:
        """
            # bot_rules (setter)

            ## Description
            Update the bot's rules. If no rules are provided (None), the bot defaults to a predefined
            ruleset. Otherwise, the new rules are stored internally.

            ## Parameters
            ```python
            new_rules: str | None
                # The new rules to be applied. Defaults to a standard rule set if None.
            ```
        """

        self.__input_rules: str | None = str(new_rules) if new_rules is not None else ChatWeaverSystemRules.default()
        self.__rules: str = self.__input_rules

    @property
    def bot_name(self) -> str:
        """
            # bot_name (getter)

            ## Description
            Retrieve the current name of the bot.
        """

        return self.__name

    @bot_name.setter
    def bot_name(self, new_name: str) -> None:
        """
            # bot_name (setter)

            ## Description
            Assign a new name to the bot. This name is also used within the bot's rules to personalize responses.

            ## Parameters
            ```python
            new_name: str
                # The new name to assign to the bot.
            ```
        """

        self.__name: str = str(new_name)

    @property
    def bot_time_format(self) -> str:
        """
            # bot_time_format (getter)

            ## Description
            Retrieve the format string used by the bot for time-based operations.
        """

        return self.__time_format

    @bot_time_format.setter
    def bot_time_format(self, new_time_format: str) -> None:
        """
            # bot_time_format (setter)

            ## Description
            Set a new time format for the bot. This format is validated by attempting to format the current time.
            If the format is invalid, a ValueError is raised.

            ## Parameters
            ```python
            new_time_format: str
                # A valid Python time format string (e.g., "%Y-%m-%d %H:%M:%S").
            ```

            ## Raises
            ```python
            ValueError
                # Raised if 'new_time_format' is not a valid time format.
            ```
        """

        try:
            time.strftime(new_time_format, time.localtime(time.time()))
            self.__time_format = new_time_format
        except:
            raise ValueError(f"<Invalid 'new_time_format' format: Expected valid time format>")

    @property
    def bot_schema(self) -> Schema | None:
        return self.__schema

    @bot_schema.setter
    def bot_schema(self, new: Schema | None) -> None:
        if not isinstance(new, (Schema, type(None))):
            raise TypeError("<Invalid 'schema' type, must be a 'Schema' object>")

        self.__schema = new


    # -------- HELPERS --------
    def get_metadata_messages(
        self,
        img_data: str | pathlib.Path | list[str | pathlib.Path] | None = None,
        file_data: str | pathlib.Path | FileObject | list[str | pathlib.Path | FileObject] | None = None
    ) -> dict[str, list[dict[str, Any]]]:
        if not ( (isinstance(img_data, list) and len(img_data) > 0 and all(isinstance(item, (str, pathlib.Path)) for item in img_data)) or isinstance(img_data, (str, pathlib.Path)) or img_data is None):
            raise TypeError("<img_data must be a string, pathlib.Path, or list of strings or pathlib.Paths>")

        if not ( (isinstance(file_data, list) and len(file_data) > 0 and all(isinstance(item, (str, pathlib.Path, FileObject)) for item in file_data)) or isinstance(file_data, (str, pathlib.Path, FileObject)) or file_data is None ):
            raise TypeError("<file_data must be a string, pathlib.Path, or list of strings or pathlib.Paths>")

        image_messages: list[dict[str, Any]] = []
        file_messages: list[dict[str, Any]] = []
        images_content: list[Any] = []
        files_content: list[Any] = []

        if img_data is not None:
            img_data = [img_data] if isinstance(img_data, (str, pathlib.Path)) else img_data
            # preparing img_data
            for i, image in enumerate(img_data):
                if is_valid_url(image):
                    img_data[i] = image
                elif is_valid_path(image):
                    img_data[i] = f"data:image/png;base64,{base64.b64encode(open(image, 'rb').read()).decode('utf-8')}"
                else:
                    raise ValueError(f"<Invalid image path: {image}>")

            for image in img_data:
                img_message = {
                    "type": "image_url",
                    "image_url": {"url": image}
                }

                image_messages.append(img_message)
                images_content.append(image)

        # ---- files ----
        if file_data is not None:
            file_list: list[str | pathlib.Path | FileObject] = [file_data] if isinstance(file_data, (str, pathlib.Path, FileObject)) else file_data

            for f in file_list:
                # 1) se è già un file_id, uso così com'è
                if is_file_id(f):
                    uploaded_id = f
                # 2) se è un path locale valido, carico
                elif is_valid_path(f):
                    with open(f, "rb") as fh:
                        uploaded = self.model_client.files.create(
                            file=fh,
                            purpose="user_data"
                        )
                    files_content.append(fh)
                    uploaded_id = uploaded.id
                # 3) rifiuto URL per i file (la Files API non prende URL diretti)
                elif isinstance(f, str) and is_valid_url(f):
                    raise ValueError(f"<Invalid file source (URL not supported for file uploads): {f}>")
                else:
                    raise ValueError(f"<Invalid file path or file_id: {f}>")

                file_messages.append({
                    "type": "file",
                    "file": {"file_id": uploaded_id}
                })

        return {
            "image_messages": image_messages,
            "file_messages": file_messages,
            "images_content": images_content,
            "files_content": files_content
        }



    # -------- ACTIONS --------
    def completion(self,
           prompt: str,
           user: str = "User",
           history: list | None = None,
           img_data: str | pathlib.Path | list[str | pathlib.Path] | None = None,
           file_data: str | pathlib.Path | FileObject | list[str | pathlib.Path | FileObject] | None = None,
           response_schema: Schema | None = None
        ) -> BotGenerationResult:
        start_date = time.strftime(self.bot_time_format, time.localtime(time.time()))  # user prompt date
        prompt = str(prompt)

        messages: list[dict[str, Any | list]] = [
            {"role": "system", "content": self.__rules + f" [User name is: {user}]"},
            {"role": "user", "content": [{"type": "text", "text": prompt}]}
        ]

        messages = [dict(message) for message in history] + messages if history is not None else messages

        # LOAD METADATA
        metadata_messages = self.get_metadata_messages(img_data=img_data, file_data=file_data)

        for image_message in metadata_messages["image_messages"]:
            messages[1]["content"].append(image_message)

        for file_message in metadata_messages["file_messages"]:
            messages[1]["content"].append(file_message)

        # SET OUTPUT SCHEMA
        if not isinstance(response_schema, (Schema, type(None))):
            raise TypeError("< 'response_schema' must be of type Schema or NoneType >")
        if response_schema is None:
            if self.bot_schema is None:
                response_schema = None
            else:
                response_schema = self.bot_schema

        start = time.perf_counter()
        response = self.model_client.chat.completions.create(
            model=self.model_model,
            messages=messages,  # type: ignore
            response_format=response_schema.resolve() if response_schema else None  # type: ignore
        )
        end = time.perf_counter()
        final_date = time.strftime(self.bot_time_format, time.localtime(time.time()))  # assistant response date

        content = response.choices[0].message.content if response.choices[0].message.content is not None else response.choices[0].message.refusal


        return BotGenerationResult(
            content=content,
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
            total_tokens=response.usage.total_tokens,
            start_date=start_date,
            delta_time=end - start,
            final_date=final_date,
            input_metadata=MetadataContainer(
                images=metadata_messages["images_content"],
                files=metadata_messages["files_content"]
            ),
            output_metadata=MetadataContainer(
                images=[],
                files=[]
            )
        )


    def generation(
            self,
            prompt: str,
            user: str = "User",
            history: list | None = None,
            img_data: str | pathlib.Path | list[str | pathlib.Path] | None = None,
            file_data: str | pathlib.Path | FileObject | list[str | pathlib.Path | FileObject] | None = None,
            response_schema: Schema | None = None
        ) -> BotGenerationResult:
        start_date = time.strftime(self.bot_time_format, time.localtime(time.time()))  # user prompt date
        prompt = str(prompt)

        start = time.perf_counter()
        end = time.perf_counter()

        final_date = time.strftime(self.bot_time_format, time.localtime(time.time()))  # assistant response date
        raise NotImplementedError
