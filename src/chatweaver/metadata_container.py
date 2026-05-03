from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class MetadataContainer:
    images: list[Any]
    files: list[Any]

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} | images: {str(self.images)}, files: {str(self.files)}>"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"images={self.images!r}, "
            f"files={self.files!r}"
            f")"
        )

    def __iter__(self):
        return iter({
            "images": self.images,
            "files": self.files
        }.items())
