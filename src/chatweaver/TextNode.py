from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TextNode:
    """
    # TextNode

    ## Description
    Represents an immutable text node with metadata attributes. A TextNode object represents a single message in a conversation.

    ## Attributes
    ```
    role: str      # The role of the TextNode ('assistant' or 'user').
    content: str   # The content of the TextNode.
    owner: str     # The owner name of the TextNode.
    tokens: int    # The number of tokens associated with the TextNode.
    date: str      # The creation date of the TextNode.
    ```

    ## Methods
    ```
    __str__() -> str   # Returns the string representation of the object in JSON-like format.
    __iter__() -> dict # Returns an iterator for the object's attributes as key-value pairs. Useful for unpacking the object with the dict() constructor.
    ```
    """

    role: str
    content: str
    owner: str
    tokens: int
    date: str
    image_data: list[Any]
    file_data: list[Any]

    def __str__(self) -> str:
        return repr({
            "role": self.role,
            "content": self.content,
            "owner": self.owner,
            "tokens": self.tokens,
            "date": self.date,
            "image_data": self.image_data,
            "file_data": self.file_data
        })

    def __iter__(self) -> dict:
        return iter(eval(self.__str__()).items())
