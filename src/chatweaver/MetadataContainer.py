from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class MetadataContainer:
    images: list[Any]
    files: list[Any]

    def __str__(self) -> str:
        return str({
            "images": self.images,
            "files": self.files
        })

    def __repr__(self) -> str:
        return self.__str__()

    def __iter__(self) -> dict:
        return iter(eval(self.__str__()).items())