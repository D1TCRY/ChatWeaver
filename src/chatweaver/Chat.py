from __future__ import annotations
from types import NoneType
from typing import Any, Union
import time

from .BotGenerationResult import BotGenerationResult
# relative imports
from .TextNode import TextNode
from .Bot import  Bot


class Chat(Bot):
    """
        # Chat

        ## Description
        Represents a chat session built upon the Bot class. This class manages conversation history,
        response generation, and chat metadata such as reply limits, creation date, and cost calculation.
        It maintains a log of messages, integrates model responses, and allows for attachments like
        images or files in the prompts.
    """

    def __init__(self,
                 *args,
                 title: str = "New Chat",
                 replies_limit: int | None = 10,
                 user: str = "User",
                 cw_bot: Bot | None = None,
                 **kwargs) -> None:
        """
            # Chat

            ## Description
            Represents a chat session built upon the Bot class. This class manages conversation history,
            response generation, and chat metadata such as reply limits, creation date, and cost calculation.
            It maintains a log of messages, integrates model responses, and allows for attachments like
            images or files in the prompts.

            ## Attributes
            ```python
            chat_time_format: str              # The time format used for chat timestamps (default: "%d/%m/%Y %H:%M:%S").
            chat_replies_limit: int            # The maximum number of replies allowed in the chat (or infinity if None).
            chat_history: list[TextNode]       # The conversation history as a list of TextNode objects.
            chat_user: str                     # The user participating in the chat session.
            chat_creation_date: str            # The timestamp when the chat was created.
            chat_replies: int                  # The current number of replies in the chat (computed from history).
            chat_cost: int                     # The total cost calculated based on the tokens used in all messages.
            chat_title: str                    # The title of the chat session.
            ```

            ## Methods
            ```python
            __init__(*args, title: str = "New Chat", replies_limit: int | None = 10, user: str = "User", cw_bot: Bot | None = None, **kwargs) -> None
                # Initializes the chat session with a title, time format, creation date, reply limit, user,
                # and optionally an existing Bot or a new Bot.

            __str__() -> str
                # Returns a user-friendly string representation of the chat, including the title, reply limit,
                # current reply count, and creation date.

            __repr__() -> str
                # Returns a formal string representation of the chat with details about its attributes
                # and the associated Bot state.

            __lt__(other: Chat) -> bool
                # Compares two Chat instances based on their creation dates for chronological ordering.

            __eq__(other: Chat) -> bool
                # Determines if two Chat instances are equal by comparing their relevant attributes
                # (reply limit, user, title, creation date, replies, history, and underlying Bot).

            chat_Bot -> Bot
                # Property to get the underlying Bot instance, granting direct access to its attributes and methods.

            chat_time_format -> str
                # Property to get the current time format used for timestamps.

            chat_replies_limit -> int
                # Property to get the maximum number of allowed replies (or infinity if None was provided).

            chat_history -> list[TextNode]
                # Property to get the conversation history, stored as a list of TextNode objects.

            chat_user -> str
                # Property to get the name of the user participating in the chat.

            chat_creation_date -> str
                # Property to get the creation date of the chat session, formatted according to 'chat_time_format'.

            chat_replies -> int
                # Property to get the number of replies (counted as user+assistant message pairs).

            chat_cost -> int
                # Property to get the total cost (sum of token usage across all messages in 'chat_history').

            chat_title -> str
                # Property to get the title of the chat session.

            set_all(return_self: bool = True, **kwargs: Any) -> None
                # Updates multiple Chat, Bot, and Model attributes at once using keyword arguments.
                # Returns the Chat instance by default for chaining.

            chat_replies_limit.setter(new_replies_limit: int | None) -> None
                # Sets a new reply limit, treating None as infinity.

            chat_history.setter(new_history: list[TextNode] | list[dict[str, str]] | None) -> None
                # Sets the conversation history, supporting both TextNode objects and dictionaries convertible to TextNode.

            chat_time_format.setter(new_time_format: str) -> None
                # Sets a new time format and validates it.

            chat_creation_date.setter(new_creation_date: str) -> None
                # Sets a new creation date, ensuring it matches the current time format.

            chat_user.setter(new_user: str) -> None
                # Updates the user participating in the chat.

            chat_title.setter(new_title: str) -> None
                # Updates the title of the chat session.

            get_response(prompt: str, user: str | None = None, image_path: str | None = None, file_path: str | None = None) -> str
                # Generates a response based on the given prompt (and optional attachments).
                # The assistant's reply is stored in the chat history.

            __update_history(prompt: str, response: dict[str, Any], owner_user: str | None) -> None
                # Internal method to append user and assistant messages to the chat history, respecting the reply limit.
            ```

            ---

            # __init__

            ## Description
            Initialize a new Chat session, setting attributes such as title, time format, creation date,
            user, and reply limits. If an existing Bot instance is not provided, a new Bot instance is
            created using the arguments passed to the constructor.

            ## Parameters
            ```python
            *args: Any
                # Positional arguments forwarded to the Bot (or Model) constructor if cw_bot is not provided.
            title: str
                # The title of the chat session (default: "New Chat").
            replies_limit: int | None
                # The maximum number of replies allowed (default: 10). If None, no limit is imposed.
            user: str
                # The user participating in the chat (default: "User").
            cw_bot: Bot | None
                # An existing Bot instance. If None, a new Bot is created with *args and **kwargs.
            **kwargs: Any
                # Additional keyword arguments passed to the Bot (or Model) constructor if cw_bot is not provided.
            ```

            ## Raises
            ```python
            TypeError
                # Raised if 'cw_bot' is provided but is not an instance of Bot.
            ```
        """

        # title
        self.chat_title = str(title)
        # time format
        self.chat_time_format = "%d/%m/%Y %H:%M:%S"
        # creation_date
        self.chat_creation_date = time.strftime(self.chat_time_format, time.localtime(time.time()))
        # replies_limit
        self.chat_replies_limit = replies_limit
        # replies
        self.__replies: int = 0
        # history
        self.chat_history = []
        # user
        self.chat_user = str(user)

        # bot
        if not isinstance(cw_bot, Bot) and cw_bot is not None:
            raise TypeError(f"<Invalid 'cw_bot' type: Expected 'Bot' instance, got {type(cw_bot)}>")
        if cw_bot == None:
            super().__init__(*args, **kwargs)
            self.__bot: Bot = Bot(*args, **kwargs)
        else:
            self.__bot: Bot = cw_bot
            super().__init__(rules=self.__bot.bot_rules, name=self.__bot.bot_name, model=self.__bot.model_model,
                             api_key=self.__bot.model_api_key)

        # default attributes
        self.__default_attributes = {
            "replies_limit": 10,
            "user": "User",
            "title": "New Chat"
        }

    # -------- MAGIC METHODS --------
    def __str__(self):
        """
            # __str__

            ## Description
            Return a user-friendly string representation of the chat session.
            This typically includes the chat title, the maximum number of replies,
            the current number of replies, and the creation date.
        """

        return f"<Chat | title={repr(self.chat_title)}, replies_limit={self.chat_replies_limit}, replies={self.chat_replies}, creation_date={repr(self.chat_creation_date)}>"

    def __repr__(self):
        """
            # __repr__

            ## Description
            Return a formal string representation of the chat, including key attributes such as
            reply limit, user, title, and the associated Bot (by calling the superclass's __repr__).
            This representation can be used for debugging or logging purposes.
        """

        is_replies_limit: bool = self.chat_replies_limit == self.__default_attributes["replies_limit"]
        is_user: bool = self.chat_user == self.__default_attributes["user"]
        is_title: bool = self.chat_title == self.__default_attributes["title"]

        str_replies_limit: str = f"replies_limit={repr(self.chat_replies_limit)}," if not is_replies_limit else ""
        str_user: str = f"user={repr(self.chat_user)}," if not is_user else ""
        str_title: str = f"title={repr(self.chat_title)}," if not is_title else ""

        return f"Chat({str_replies_limit} {str_user} {str_title} cw_bot={super().__repr__()}).set_all(_Chat__history={self.chat_history}, _Chat__creation_date={repr(self.chat_creation_date)})"

    def __lt__(self, other) -> bool:
        """
            # __lt__

            ## Description
            Compare this Chat instance to another Chat instance based on their creation dates.
            This method allows sorting Chat objects chronologically.

            ## Parameters
            ```python
            other: Chat
                # The Chat instance to compare against the current one.
            ```

            ## Returns
            ```python
            bool
                # True if this Chat's creation date is earlier than the other Chat's creation date, False otherwise.
            ```
        """

        # Convert the string to a time object and compare
        self_time = time.strptime(self.chat_creation_date, self.chat_time_format)
        other_time = time.strptime(other.chat_creation_date, self.chat_time_format)
        return self_time < other_time

    def __eq__(self, other) -> bool:
        """
            # __eq__

            ## Description
            Compare this Chat instance to another Chat instance for equality. Two chats are considered
            equal if they have the same reply limit, user, title, creation date, number of replies,
            conversation history, and underlying Bot.

            ## Parameters
            ```python
            other: Chat
                # The Chat instance to compare against the current one.
            ```

            ## Returns
            ```python
            bool
                # True if all chat attributes match; False otherwise.
            ```
        """

        is_replies_limit = self.chat_replies_limit == other.chat_replies_limit
        is_user = self.chat_user == other.chat_user
        is_title = self.chat_title == other.chat_title

        is_creation_date = self.chat_creation_date == other.chat_creation_date
        is_replies = self.chat_replies == other.chat_replies
        is_history = self.chat_history == other.chat_history

        is_bot = eval(self.chat_Bot.__repr__()) == eval(other.chat_Bot.__repr__())

        return is_replies_limit and is_user and is_title and is_creation_date and is_replies and is_history and is_bot

    # -------- GET --------
    # CHAT_BOT
    @property
    def chat_Bot(self) -> Bot:
        """
            # chat_Bot (getter)

            ## Description
            Retrieve the Bot instance associated with this Chat by invoking the superclass.
            This allows direct access to the underlying bot's attributes and methods.
        """

        return super()

    # CHAT_TIME_FORMAT
    @property
    def chat_time_format(self) -> str:
        """
            # chat_time_format (getter)

            ## Description
            Retrieve the current time format used by this Chat for timestamps, such as creation date
            and message logs.
        """

        return self.__time_format

    @chat_time_format.setter
    def chat_time_format(self, new_time_format: str) -> None:
        """
            # chat_time_format (setter)

            ## Description
            Update the time format used by this chat for timestamps.
            Attempts to format the current time with the new format to ensure validity.

            ## Parameters
            ```python
            new_time_format: str
                # A valid Python time format string (e.g., "%d/%m/%Y %H:%M:%S").
            ```

            ## Raises
            ```python
            ValueError
                # Raised if the format string cannot be used to format the current time.
            ```
        """

        try:
            time.strftime(new_time_format, time.localtime(time.time()))
            self.__time_format = new_time_format
        except:
            raise ValueError(f"<Invalid 'new_time_format' format: Expected valid time format>")

    # CHAT_REPLIES_LIMIT
    @property
    def chat_replies_limit(self) -> float | int:
        """
            # chat_replies_limit (getter)

            ## Description
            Retrieve the maximum number of replies allowed in this chat. If no limit is set
            (i.e., None was provided), the value is represented internally as infinity.
        """

        return self.__replies_limit

    @chat_replies_limit.setter
    def chat_replies_limit(self, new_replies_limit: int | None) -> None:
        """
            # chat_replies_limit (setter)

            ## Description
            Set a new reply limit for the chat. If None is provided, the limit is treated as infinity.

            ## Parameters
            ```python
            new_replies_limit: int | None
                # The new reply limit. If None, there is no limit.
            ```

            ## Raises
            ```python
            TypeError
                # Raised if the new value cannot be converted to an integer when it is not None.
            ```
        """

        try:
            self.__replies_limit = float("inf") if new_replies_limit is None else int(new_replies_limit)
        except:
            raise TypeError(f"<Invalid 'new_replies_limit' format: Expected 'int', got {type(new_replies_limit)}>")

    # CHAT_HISTORY
    @property
    def chat_history(self) -> list[TextNode]:
        """
            # chat_history (getter)

            ## Description
            Retrieve the chat's conversation history, stored as a list of TextNode objects.
            Each TextNode contains information such as the role (user or assistant), content, owner,
            token count, and timestamp.
        """

        return self.__history

    @chat_history.setter
    def chat_history(self, new_history: list[TextNode] | list[dict[str, str]] | None) -> None:
        """
            # chat_history (setter)

            ## Description
            Set a new conversation history for the chat. The history can be a list of TextNode objects or
            a list of dictionaries convertible into TextNode objects.

            ## Parameters
            ```python
            new_history: list[TextNode] | list[dict[str, str]] | None
                # A list of TextNode objects or dictionaries defining message content. If None or empty,
                # the chat history is reset to an empty list.
            ```

            ## Raises
            ```python
            TypeError
                # Raised if the elements in new_history are neither TextNode nor dict,
                # or if the dict structure is invalid for converting to a TextNode.
            ```
        """

        if new_history is not None:
            if not isinstance(new_history, list):
                raise TypeError("< 'new_history' must be a list >")

            if all(isinstance(node, TextNode) for node in new_history):
                self.__history: list[TextNode] = new_history  # type: ignore
            elif all([isinstance(node, dict) for node in new_history]):
                try:
                    self.__history: list[TextNode] = [TextNode(**node) for node in new_history]  # type: ignore
                except:
                    raise TypeError("<Invalid 'new_history' format>")
            else:
                raise TypeError("<Invalid 'new_history' format>")
        else:
            self.__history: list[TextNode] = []

    # CHAT_USER
    @property
    def chat_user(self) -> str:
        """
            # chat_user (getter)

            ## Description
            Retrieve the name of the user participating in the chat session.
        """

        return self.__user

    @chat_user.setter
    def chat_user(self, new_user: str) -> None:
        """
            # chat_user (setter)

            ## Description
            Update the user participating in the chat session.

            ## Parameters
            ```python
            new_user: str
                # The name or identifier of the new user.
            ```
        """

        self.__user = str(new_user)

    # CHAT_CREATION_DATE
    @property
    def chat_creation_date(self) -> str:
        """
            # chat_creation_date (getter)

            ## Description
            Retrieve the creation date of the chat session, formatted according to `chat_time_format`.
        """

        return self.__creation_date

    @chat_creation_date.setter
    def chat_creation_date(self, new_creation_date: str) -> None:
        """
            # chat_creation_date (setter)

            ## Description
            Set a new creation date for the chat. The date must match the current `chat_time_format`.

            ## Parameters
            ```python
            new_creation_date: str
                # A date string conforming to chat_time_format.
            ```

            ## Raises
            ```python
            ValueError
                # Raised if the provided date string does not match the chat_time_format.
            ```
        """

        # check if new_creation_date is a valid date format
        try:
            # try to convert the string to a datetime object
            time.strptime(new_creation_date, self.chat_time_format)
            self.__creation_date = new_creation_date
        except:
            raise ValueError(f"<Invalid 'new_creation_date' format: Expected {repr(self.chat_time_format)}>")

    # CHAT_REPLIES
    @property
    def chat_replies(self) -> int:
        """
            # chat_replies (getter)

            ## Description
            Retrieve the number of replies in the conversation. This value is computed as
            half the length of the chat history, since each user message and bot response
            together count as one "reply."
        """

        self.__replies = len(self.__history) // 2
        return self.__replies

    # CHAT_COST
    @property
    def chat_cost(self) -> int:
        """
            # chat_cost (getter)

            ## Description
            Retrieve the total cost of the chat. This value is calculated by summing the token
            counts of all TextNode entries in the chat's history.
        """

        return sum([node.tokens for node in self.chat_history])

    # CHAT_TITLE
    @property
    def chat_title(self) -> str:
        """
            # chat_title (getter)

            ## Description
            Retrieve the chat session's title.
        """

        return self.__title

    @chat_title.setter
    def chat_title(self, new_title: str) -> None:
        """
            # chat_title (setter)

            ## Description
            Update the chat session's title.

            ## Parameters
            ```python
            new_title: str
                # The new title for the chat.
            ```
        """

        self.__title = str(new_title)

    # -------- SET --------
    def set_all(self, return_self: bool = True, **kwargs: Any) -> Union[Chat | NoneType]:
        """
            # set_all

            ## Description
            Update multiple attributes of the Chat (and its underlying Bot and Model) based on
            the provided keyword arguments. This function iterates through all attributes
            and updates them accordingly. By default, it returns `self` for easy method chaining.

            ## Parameters
            ```python
            return_self: bool = True
                # If True, returns the Chat instance itself after updates; otherwise, returns None.
            **kwargs: Any
                # Keyword arguments where each key corresponds to a private attribute path
                # (e.g., "_Chat__user", "_Bot__rules", or "_Model__api_key") and each value is the new value to set.
            ```

            ## Returns
            ```python
            Chat | None
                # Returns self if return_self is True, otherwise None.
            ```
        """

        for key, value in kwargs.items():
            match key:
                # Chat
                case "_Chat__replies_limit":
                    self.chat_replies_limit = value
                case "_Chat__history":
                    self.chat_history = value
                case "_Chat__creation_date":
                    self.chat_creation_date = value
                case "_Chat__user":
                    self.chat_user = value
                case "_Chat__title":
                    self.chat_title = value
                # Bot
                case "_Bot__rules":
                    self.bot_rules = value
                case "_Bot__name":
                    self.bot_name = value
                # Model
                case "_Model__model":
                    self.model_model = value
                case "_Model__api_key":
                    self.model_api_key = value

        return self if return_self else None

    # -------- ACTIONS --------
    def response(self,
                 prompt: str,
                 user: str | None = None,
                 image_path: str | None = None,
                 file_path: str | None = None) -> str:
        """
            # response

            ## Description
            Generate a response for a given user prompt. Optionally, an image or file can be attached
            for context. The returned text is then appended to the chat history as two TextNode objects
            (one for the user and one for the assistant).

            ## Parameters
            ```python
            prompt: str
                # The user's message to the chat.
            user: str | None = None
                # The name or identifier of the user for this prompt. Defaults to the chat_user if None.
            image_path: str | None = None
                # The path to an image file to be base64-encoded and attached to the prompt.
            file_path: str | None = None
                # The path to a file to be uploaded and referenced by the underlying bot.
            ```

            ## Returns
            ```python
            str
                # The assistant's response content.
            ```
        """

        response = self.completion(prompt=prompt,
                                   user=self.__user if user is None else str(user),
                                   history=self.__history if self.__history else None,
                                   img_data=image_path,
                                   file_data=file_path)

        self.__update_history(prompt=prompt, response=response, owner_user=user)
        return response.content

    def __update_history(self, prompt: str, response: BotGenerationResult, owner_user: str | None = None) -> None:
        """
            # __update_history

            ## Description
            A private method that updates the conversation history with a new user prompt and
            the corresponding assistant response. Each conversation turn consists of two TextNode objects:
            one for the user and one for the assistant. If the reply limit is reached, this method
            removes the oldest user and assistant messages from the history before appending the new ones.

            ## Parameters
            ```python
            prompt: str
                # The user's message to append to the chat history.
            response: dict[str, Any]
                # The dictionary containing response content and metadata returned by the underlying bot.
            owner_user: str | None
                # The name or identifier of the user for this prompt. Defaults to chat_user if None.
            ```
        """

        owner_user = self.__user if owner_user is None else str(owner_user)

        user_node: TextNode = TextNode(
            role="user",
            content=prompt,
            owner=owner_user,
            tokens=response.prompt_tokens,
            date=response.start_date,
            image_data=response.input_metadata.images,
            file_data=response.input_metadata.files
        )

        assistant_node: TextNode = TextNode(
            role="assistant",
            content=response.content,
            owner=self.bot_name,
            tokens=response.completion_tokens,
            date=response.final_date,
            image_data=response.output_metadata.images,
            file_data=response.output_metadata.files
        )

        if self.__replies + 1 <= self.__replies_limit:
            self.__replies: int = self.__replies + 1

            self.__history.append(user_node)
            self.__history.append(assistant_node)
        else:
            self.__history.pop(0)
            self.__history.pop(0)

            self.__history.append(user_node)
            self.__history.append(assistant_node)

