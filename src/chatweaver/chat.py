from __future__ import annotations

from types import NoneType
from typing import Any, Union, Optional
import time

from .bot_completion_result import BotCompletionResult
from .text_node import TextNode
from .bot import Bot


class Chat(object):
    """
    A chat session that uses a provided Bot instance.
    """

    def __init__(
        self,
        bot: Optional[Bot] = None,
        title: str = "New Chat",
        replies_limit: int | None = 10,
        user: str = "User",
        time_format: str = "%d/%m/%Y %H:%M:%S",
        creation_date: Optional[str] = None,
        history: Optional[list[TextNode] | list[dict[str, Any]]] = None,
        **kwargs,
    ) -> None:
        """
        Create a chat session with history and basic metadata.
        """

        self.__default_attributes: dict[str, Any] = {
            "replies_limit": 10,
            "user": "User",
            "title": "New Chat",
            "time_format": "%d/%m/%Y %H:%M:%S",
        }

        # Restore from snapshot
        if "define" in kwargs:
            attributes: dict[str, dict[str, Any]] = kwargs["define"]
            props: dict[str, Any] = attributes.get("properties", {})
            extra: dict[str, Any] = attributes.get("extra", {})

            # Go through setters for validation and dunder initialization
            for k, v in props.items():
                setattr(self, k, v)
            for k, v in extra.items():
                setattr(self, k, v)

            if getattr(self, "_Chat__bot", None) is None:
                raise ValueError("<Invalid snapshot: missing 'bot'>")

            return

        # Normal init
        self.time_format = time_format
        self.title = title
        self.replies_limit = replies_limit
        self.user = user
        self.history = history

        self.bot = bot if bot is not None else Bot()

        if creation_date is None:
            self.creation_date = time.strftime(self.time_format, time.localtime(time.time()))
        else:
            self.creation_date = creation_date

    # -------- FREEZE / THAW --------
    def freeze(self, include_secrets: bool = False) -> dict[str, Any]:
        """
        Return a serializable snapshot of the chat.
        Secrets are excluded by default.
        """
        return {
            "properties": {
                "title": self.title,
                "user": self.user,
                "time_format": self.time_format,
                "creation_date": self.creation_date,
                "replies_limit": None if self.__replies_limit == float("inf") else int(self.__replies_limit),
                "history": [node.freeze() for node in self.history],
                "bot": self.bot.freeze(include_secrets=include_secrets),
            },
            "extra": {},
        }

    @classmethod
    def thaw(
        cls,
        snapshot: dict[str, Any],
        bot: Optional[Bot] = None,
        api_key: Optional[str] = None,
    ) -> "Chat":
        """
        Restore a chat from a snapshot.
        """
        if not isinstance(snapshot, dict):
            raise TypeError("<Invalid snapshot: expected dict>")

        props = snapshot.get("properties", {})
        if not isinstance(props, dict):
            raise ValueError("<Invalid snapshot: missing properties dict>")

        # Restore / select bot
        bot_snapshot = props.get("bot")
        if bot is None:
            if not isinstance(bot_snapshot, dict):
                raise ValueError("<Invalid snapshot: missing bot snapshot>")
            bot = Bot.thaw(bot_snapshot, api_key=api_key)
        else:
            # Optional override of the provided bot model api_key
            if api_key is not None:
                bot.model.api_key = api_key

        # Restore history
        history_snap = props.get("history", [])
        if not isinstance(history_snap, list):
            raise ValueError("<Invalid snapshot: history must be a list>")

        history_nodes: list[TextNode] = []
        for item in history_snap:
            if isinstance(item, dict) and "properties" in item:
                history_nodes.append(TextNode.thaw(item))
            elif isinstance(item, dict):
                # Allow legacy plain dict nodes
                history_nodes.append(TextNode(**item))  # type: ignore[arg-type]
            else:
                raise ValueError("<Invalid snapshot: invalid history item>")

        define = {
            "properties": {
                "title": props.get("title", "New Chat"),
                "user": props.get("user", "User"),
                "time_format": props.get("time_format", "%d/%m/%Y %H:%M:%S"),
                "creation_date": props.get("creation_date"),
                "replies_limit": props.get("replies_limit", 10),
                "history": history_nodes,
                "bot": bot,
            },
            "extra": snapshot.get("extra", {}),
        }

        return cls(define=define)

    # -------- MAGIC METHODS --------
    def __str__(self) -> str:
        return (
            f"<{self.__class__.__name__} | title: {self.title!r}, replies_limit: {self.replies_limit}, "
            f"replies={self.replies}, creation_date={self.creation_date!r}, api_key={self.bot.model.api_key_hint()!r}>"
        )

    def __repr__(self) -> str:
        is_replies_limit: bool = (None if self.__replies_limit == float("inf") else int(self.__replies_limit)) == self.__default_attributes["replies_limit"]
        is_user: bool = self.user == self.__default_attributes["user"]
        is_title: bool = self.title == self.__default_attributes["title"]
        is_time: bool = self.time_format == self.__default_attributes["time_format"]

        parts: list[str] = []
        if not is_title:
            parts.append(f"title={self.title!r}")
        if not is_user:
            parts.append(f"user={self.user!r}")
        if not is_time:
            parts.append(f"time_format={self.time_format!r}")
        if not is_replies_limit:
            parts.append(f"replies_limit={None if self.__replies_limit == float('inf') else int(self.__replies_limit)!r}")

        parts.append(f"bot={self.bot!r}")
        parts.append(f"creation_date={self.creation_date!r}")
        parts.append(f"history={self.history!r}")

        return f"{self.__class__.__name__}({', '.join(parts)})"

    def __lt__(self, other: "Chat") -> bool:
        self_time = time.strptime(self.creation_date, self.time_format)
        other_time = time.strptime(other.creation_date, other.time_format)
        return self_time < other_time

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Chat):
            return False

        return (
            self.title == other.title
            and self.user == other.user
            and self.time_format == other.time_format
            and self.creation_date == other.creation_date
            and self.replies_limit == other.replies_limit
            and self.history == other.history
            and self.bot == other.bot
        )

    # -------- PROPERTIES --------
    @property
    def bot(self) -> Bot:
        """Return the bot used by this chat."""
        return self.__bot
    @bot.setter
    def bot(self, new: Bot) -> None:
        """Set the bot used by this chat."""
        if not isinstance(new, Bot):
            raise TypeError(f"<Invalid 'bot' type: Expected Bot, got {type(new)}>")

        self.__bot = new

    @property
    def time_format(self) -> str:
        """Return the time format used for timestamps."""
        return self.__time_format
    @time_format.setter
    def time_format(self, new_time_format: str) -> None:
        """Set and validate the time format string."""
        try:
            time.strftime(str(new_time_format), time.localtime(time.time()))
            self.__time_format = str(new_time_format)
        except Exception:
            raise ValueError("<Invalid 'time_format': expected valid strftime format>")

    @property
    def replies_limit(self) -> float | int:
        """Return the maximum number of replies allowed."""
        return self.__replies_limit
    @replies_limit.setter
    def replies_limit(self, new_replies_limit: int | None) -> None:
        """Set the reply limit. None means no limit."""
        try:
            self.__replies_limit = float("inf") if new_replies_limit is None else int(new_replies_limit)
        except Exception:
            raise TypeError(f"<Invalid 'replies_limit': Expected int or None, got {type(new_replies_limit)}>")

    @property
    def history(self) -> list[TextNode]:
        """Return the message history."""
        return self.__history
    @history.setter
    def history(self, new_history: list[TextNode] | list[dict[str, Any]] | None) -> None:
        """Set the chat history."""
        if new_history is None:
            self.__history = []
            return

        if not isinstance(new_history, list):
            raise TypeError("<'history' must be a list>")

        if len(new_history) == 0:
            self.__history = []
            return

        if all(isinstance(node, TextNode) for node in new_history):
            self.__history = list(new_history)  # type: ignore[assignment]
            return

        if all(isinstance(node, dict) for node in new_history):
            try:
                # Accept either frozen snapshots or plain dict node payloads
                nodes: list[TextNode] = []
                for node in new_history:
                    if "properties" in node and "version" in node:
                        nodes.append(TextNode.thaw(node))  # type: ignore[arg-type]
                    else:
                        nodes.append(TextNode(**node))  # type: ignore[arg-type]
                self.__history = nodes
            except Exception:
                raise TypeError("<Invalid 'history' format>")
            return

        raise TypeError("<Invalid 'history' format>")

    @property
    def user(self) -> str:
        """Return the user name for this chat."""
        return self.__user
    @user.setter
    def user(self, new_user: str) -> None:
        """Set the user name for this chat."""
        new_user = str(new_user).strip()
        if len(new_user) == 0:
            raise ValueError("<Invalid 'user': cannot be empty>")
        self.__user = new_user

    @property
    def creation_date(self) -> str:
        """Return the creation date of the chat."""
        return self.__creation_date
    @creation_date.setter
    def creation_date(self, new_creation_date: str) -> None:
        """Set and validate the creation date string."""
        try:
            time.strptime(str(new_creation_date), self.time_format)
            self.__creation_date = str(new_creation_date)
        except Exception:
            raise ValueError(f"<Invalid 'creation_date': expected format {self.time_format!r}>")

    @property
    def title(self) -> str:
        """Return the chat title."""
        return self.__title
    @title.setter
    def title(self, new_title: str) -> None:
        """Set the chat title."""
        new_title = str(new_title).strip()
        if len(new_title) == 0:
            raise ValueError("<Invalid 'title': cannot be empty>")
        self.__title = new_title

    @property
    def replies(self) -> int:
        """Return the current number of replies."""
        return len(self.__history) // 2
    @property
    def cost(self) -> int:
        """Return the total token cost accumulated in history."""
        return sum(node.tokens for node in self.__history)

    # -------- ACTIONS --------
    def response(
        self,
        prompt: str,
        user: Optional[str] = None,
        image_path: Optional[str] = None,
        file_path: Optional[str] = None,
    ) -> str:
        """
        Generate a response and append it to history.
        """
        owner_user = self.__user if user is None else str(user)

        result = self.bot.completion(
            prompt=str(prompt),
            user=owner_user,
            history=[dict(node) for node in self.__history] if self.__history else None,
            img_data=image_path,
            file_data=file_path,
        )

        self.__update_history(prompt=str(prompt), response=result, owner_user=owner_user)
        return result.content

    def __update_history(self, prompt: str, response: BotCompletionResult, owner_user: str) -> None:
        """
        Append the latest user prompt and assistant response to history.
        """
        user_node = TextNode(
            role="user",
            content=str(prompt),
            owner=str(owner_user),
            tokens=int(response.prompt_tokens),
            date=str(response.start_date),
            image_data=list(response.input_metadata.images),
            file_data=list(response.input_metadata.files),
        )

        assistant_node = TextNode(
            role="assistant",
            content=str(response.content),
            owner=str(self.bot.name),
            tokens=int(response.completion_tokens),
            date=str(response.final_date),
            image_data=list(response.output_metadata.images),
            file_data=list(response.output_metadata.files),
        )

        # Enforce reply limit (each reply is 2 nodes)
        next_replies = (len(self.__history) // 2) + 1
        if next_replies <= self.__replies_limit:
            self.__history.append(user_node)
            self.__history.append(assistant_node)
            return

        # Drop the oldest pair and append the new pair
        if len(self.__history) >= 2:
            self.__history.pop(0)
            self.__history.pop(0)
        self.__history.append(user_node)
        self.__history.append(assistant_node)
