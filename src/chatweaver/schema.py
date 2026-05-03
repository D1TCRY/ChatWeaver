from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Schema:
    """
    A simple JSON schema container for structured model outputs.
    """
    name: str
    properties: dict[str, Any]

    @property
    def required(self) -> list[str]:
        return [k for k in self.properties]

    def resolve(self) -> dict:
        """
        Return an OpenAI-compatible response_format schema.
        """
        return {
            "type": "json_schema",
            "json_schema": {
                "name": self.name,
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": self.properties,
                    "required": self.required,
                    "additionalProperties": False
                }
            }
        }

    # -------- Freeze / Thaw --------
    def freeze(self) -> dict[str, Any]:
        """
        Return a serializable snapshot of this schema.
        """
        return {
            "version": 1,
            "properties": {
                "name": self.name,
                "properties": self.properties
            },
            "extra": {}
        }

    @classmethod
    def thaw(cls, snapshot: dict[str, Any]) -> "Schema":
        """
        Restore a Schema from a snapshot.
        """
        if not isinstance(snapshot, dict):
            raise TypeError("<Invalid snapshot: expected dict>")

        props = snapshot.get("properties", {})
        name = props.get("name")
        properties = props.get("properties")

        if not isinstance(name, str) or len(name.strip()) == 0:
            raise ValueError("<Invalid schema snapshot: missing or invalid 'name'>")
        if not isinstance(properties, dict):
            raise ValueError("<Invalid schema snapshot: missing or invalid 'properties'>")

        return cls(name=str(name), properties=properties)
