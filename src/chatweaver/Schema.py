from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class Schema:
    name: str
    properties: dict[str, Any]

    @property
    def required(self) -> list[str]:
        return [k for k in self.properties]

    def resolve(self) -> dict:
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
