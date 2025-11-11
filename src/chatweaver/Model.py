from typing import Any
from .data import ChatWeaverModelNames
import openai



cache_api_key = set()
cache_model_name = set()


class Model(object):
    """
        # Model

        ## Description
        A convenient wrapper class for managing AI models and their API keys. This class provides methods
        for defining, validating, and working with OpenAI-based API clients, ensuring that both the model
        name and the API key are correctly set and tested before use.
    """

    def __init__(self,
            api_key: str,
            model: str = ChatWeaverModelNames.gpt_4o,
            **kwargs
        ) -> None:
        """
        # Model

        ## Description
        A convenient wrapper class for managing AI models and their API keys. This class provides methods
        for defining, validating, and working with OpenAI-based API clients, ensuring that both the model
        name and the API key are correctly set and tested before use.

        ## Attributes
        ```python
        model_api_key: str            # Public attribute for retrieving or setting the API key.
        model_model: str              # Public attribute for retrieving or setting the model name.
        __default_attributes: dict    # Internal dictionary storing default attribute values (e.g., default model name).
        __model: str                  # Private attribute holding the model name after validation.
        __api_key: str                # Private attribute holding the validated API key.
        __client: openai.OpenAI       # Private attribute storing the initialized OpenAI client.
        ```

        ## Methods
        ```python
        __str__() -> str
            # Returns a human-readable string showing the model name and partially hidden API key.

        __repr__() -> str
            # Returns a formal string representation of the Model instance.

        __eq__(other: Model) -> bool
            # Checks for equality by comparing both the model name and the API key.

        model_model -> str
            # Getter property for retrieving the current model name.

        model_api_key -> str
            # Getter property for retrieving the current API key.

        model_client -> openai.OpenAI
            # Getter property for retrieving the associated OpenAI client.

        model_model.setter(new_model: str) -> None
            # Setter property that validates and assigns a new model name, updating a global cache if necessary.

        model_api_key.setter(new_api_key: str) -> None
            # Setter property that validates the API key, tests connectivity, and updates the global cache before initializing a new OpenAI client.

        model_client.setter(api_key: str) -> None
            # Setter property that explicitly sets the OpenAI client, ensuring the API key matches the stored one.
        ```

        ---

        # __init__

        ## Description
        Initialize the Model instance with a given API key and an optional model name.
        The model name defaults to "gpt-4o" if not provided.

        ## Parameters
        ```
        api_key: str
            # The API key for authenticating requests. Must start with 'sk-' and be at least 20 characters long.
        model: str = "gpt-4o"
            # The name of the model to be used (defaults to "gpt-4o").
        ```

        ## Raises
        ```
        Exception
            # Raised if the provided model name is invalid or if the API key fails validation.
        ```
        """

        if "define" in kwargs:
            attributes: dict[str, dict[str, Any]] = kwargs["define"]
            properties: dict[str, Any] = attributes.get("properties", {})
            extra: dict[str, Any] = attributes.get("extra", {})

            try:
                for property_, value_ in properties.items():
                    setattr(self, property_, value_)

                for attribute_, value_ in extra.items():
                    setattr(self, attribute_, value_)

                return
            except Exception as e:
                raise Exception(f"< Error while initializing Model: {e} >")

        self.__client: openai.OpenAI | None = None

        self.model_api_key = str(api_key)
        self.model_model = str(model)

        self.__default_attributes: dict[str, Any] = {
            "model": ChatWeaverModelNames.gpt_4o
        }

    # -------- DEFINSERS --------
    def get_parameters(self) -> dict[str, Any]:
        return {
            "properties": {
                "model_api_key": self.model_api_key,
                "model_model": self.model_model
            },
            "extra": {

            }
        }

    def set_parameters(self, parameters: dict[str, Any]) -> None:
        for key, value in parameters.items():
            setattr(self, key, value)

    # -------- MAGIC METHODS --------
    def __str__(self) -> str:
        """
            # __str__

            ## Description
            Return a human-readable string representation of the Model instance,
            displaying the current model name and API key.
        """

        return f"<{self.__class__.__name__} | model={self.__model}, api_key={self.__api_key[:8]}...{self.__api_key[-8:]}>"

    def __repr__(self) -> str:
        """
            # __repr__

            ## Description
            Return a formal string representation of the Model instance, suitable for
            logging and debugging. This output includes the model name (if different
            from the default) and the API key.
        """

        is_model: bool = self.model_model == self.__default_attributes["model"]

        str_model: str = f"model={repr(self.model_model)}, " if not is_model else ""

        return f"{self.__class__.__name__}({str_model}api_key={repr(self.__api_key)})"

    def __eq__(self, other) -> bool:
        """
            # __eq__

            ## Description
            Compare this Model instance with another Model instance for equality.
            Two Model instances are considered equal if they share the same model name
            and the same API key.

            ## Parameters
            ```
            other: Model
                # The object to compare with the current Model instance.
            ```
        """

        if not isinstance(other, type(self)):
            return False

        is_model: bool = self.model_model == other.model_model
        is_api_key: bool = self.model_api_key == other.model_api_key

        return is_model and is_api_key

    # -------- GET --------
    @property
    def model_model(self) -> str:
        """
            # model_model (getter)

            ## Description
            Retrieve the name of the AI model currently in use.
        """

        return self.__model

    @model_model.setter
    def model_model(self, new_model: str) -> None:
        """
            # model_model (setter)

            ## Description
            Set the model name for the AI. This method checks if the new model name is already
            cached, and if not, it verifies the name against an allowed list of model names.
            If valid, it stores the new model name and updates a global cache.

            ## Parameters
            ```
            new_model: str
                # The new model name to set.
            ```

            ## Raises
            ```
            Exception
                # Raised if 'new_model' is not among the acceptable model names.
            ```
        """

        global cache_model_name
        new_model = str(new_model)
        if new_model not in cache_model_name:
            if new_model not in ChatWeaverModelNames.get_all_models():
                raise Exception(f"'{new_model}' is not acceptable.")
            self.__model: str = new_model
            cache_model_name.add(self.__model)
        else:
            self.__model: str = new_model

    @property
    def model_api_key(self) -> str:
        """
            # model_api_key (getter)

            ## Description
            Retrieve the current API key used by the Model instance.
        """

        return self.__api_key

    @model_api_key.setter
    def model_api_key(self, new_api_key: str) -> None:
        """
            # model_api_key (setter)

            ## Description
            Set the API key for the Model instance. This method verifies the API key format,
            checks if it is already cached, and if not, it performs a test request to ensure
            the key is valid. Upon success, it initializes a new OpenAI client.

            ## Parameters
            ```
            new_api_key: str
                # The new API key to set (must start with 'sk-' and be at least 20 characters).
            ```

            ## Raises
            ```
            ValueError
                # Raised if the API key format is invalid.
            Exception
                # Raised if there is an issue with the test request or any other validation failure.
            ```
        """

        global cache_api_key
        new_api_key = str(new_api_key)

        if new_api_key not in cache_api_key:
            try:
                if not new_api_key.startswith("sk-") or len(new_api_key) < 20:
                    raise ValueError("Invalid API key format.")

                openai.OpenAI(api_key=new_api_key).chat.completions.list()
            except Exception as e:
                self.__is_api_key_modified = True
                raise Exception(f"Invalid API key: {e}")

            cache_api_key.add(new_api_key)
            self.__api_key = new_api_key
            self.model_client = new_api_key
        else:
            try:
                self.__api_key = new_api_key
                self.model_client = new_api_key
            except Exception as e:
                cache_api_key.remove(new_api_key)
                raise Exception(f"Invalid API key: {e}")

    @property
    def model_client(self) -> openai.OpenAI:
        """
            # model_client (getter)

            ## Description
            Retrieve the OpenAI client instance associated with this Model.
            The client is automatically created whenever the API key is set or updated.
        """

        return self.__client

    @model_client.setter
    def model_client(self, api_key: str) -> None:
        """
            # model_client (setter)

            ## Description
            Explicitly set the OpenAI client by providing an API key. If the key matches
            the Model instance's current API key, a new OpenAI client is created. Otherwise,
            an exception is raised because the correct way to change the API key is via
            the 'model_api_key' property.

            ## Parameters
            ```
            api_key: str
                # The API key used to initialize the new OpenAI client. Must match the current stored API key.
            ```

            ## Raises
            ```
            Exception
                # Raised if the provided 'api_key' does not match the stored Model API key.
            ```
        """

        if self.model_api_key == api_key:
            self.__client = openai.OpenAI(api_key=api_key)
        else:
            raise Exception(f"<If you're trying to change the api_key, please do it from the model_api_key property>")



if __name__ == "__main__":
    my_api = "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"
    model = Model(api_key=my_api, model=ChatWeaverModelNames.gpt_4o)
