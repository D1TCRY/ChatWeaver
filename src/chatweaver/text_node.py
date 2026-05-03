from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TextNode:
    """
    An immutable message node with metadata.
    """
    role: str
    content: str
    owner: str
    tokens: int
    date: str
    image_data: list[Any]
    file_data: list[Any]

    def __str__(self) -> str:
        return (f"<{self.__class__.__name__} | "
                f"role: {self.role}, "
                f"content: {(self.content[:61]+'...' if len(self.content) > 64 else self.content)!r}, "
                f"owner: {self.owner!r}, "
                f"tokens: {self.tokens}, "
                f"date: {self.date}, "
                f"image_data: {self.image_data}, "
                f"file_data: {self.file_data}"
                f">")

    def __iter__(self):
        """
        Yield key-value pairs for dict(...) conversion.
        """
        yield from {
            "role": self.role,
            "content": self.content,
            "owner": self.owner,
            "tokens": self.tokens,
            "date": self.date,
            "image_data": self.image_data,
            "file_data": self.file_data
        }.items()

    # -------- FREEZE / THAW --------
    def freeze(self) -> dict[str, Any]:
        """
        Return a serializable snapshot of this node.
        """
        return {
            "version": 1,
            "properties": {
                "role": self.role,
                "content": self.content,
                "owner": self.owner,
                "tokens": self.tokens,
                "date": self.date,
                "image_data": self.image_data,
                "file_data": self.file_data,
            },
            "extra": {},
        }

    @classmethod
    def thaw(cls, snapshot: dict[str, Any]) -> "TextNode":
        """
        Restore a node from a snapshot.
        """
        if not isinstance(snapshot, dict):
            raise TypeError("<Invalid snapshot: expected dict>")

        props = snapshot.get("properties", {})
        if not isinstance(props, dict):
            raise ValueError("<Invalid snapshot: missing properties dict>")

        return cls(
            role=str(props.get("role", "")),
            content=str(props.get("content", "")),
            owner=str(props.get("owner", "")),
            tokens=int(props.get("tokens", 0)),
            date=str(props.get("date", "")),
            image_data=list(props.get("image_data", [])),
            file_data=list(props.get("file_data", [])),
        )
