from dataclasses import dataclass
from .MetadataContainer import MetadataContainer


@dataclass(frozen=True)
class BotGenerationResult:
    content: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    start_date: str
    delta_time: float
    final_date: str
    input_metadata: MetadataContainer
    output_metadata: MetadataContainer

    def __str__(self) -> str:
        return str({
            "content": self.content,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "start_date": self.start_date,
            "delta_time": self.delta_time,
            "final_date": self.final_date,
            "input_metadata": self.input_metadata,
            "output_metadata": self.output_metadata
        })

    def __repr__(self) -> str:
        return self.__str__()

    def __iter__(self) -> dict:
        return iter(eval(self.__str__()).items())