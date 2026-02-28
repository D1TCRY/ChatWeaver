from dataclasses import dataclass
from .metadata_container import MetadataContainer


@dataclass(frozen=True)
class BotCompletionResult:
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
        return (f"<{self.__class__.__name__} | "
                f"content: {(self.content[:61]+'...' if len(self.content) >= 64 else self.content)!r}, "
                f"prompt_tokens: {self.prompt_tokens}, "
                f"completion_tokens: {self.completion_tokens}, "
                f"total_tokens: {self.total_tokens}, "
                f"start_date: {self.start_date}, "
                f"delta_time: {self.delta_time:.2f}s, "
                f"final_date: {self.final_date}, "
                f"input_metadata: {self.input_metadata}, "
                f"output_metadata: {self.output_metadata}"
                f">")

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"content={self.content!r}, "
            f"prompt_tokens={self.prompt_tokens!r}, "
            f"completion_tokens={self.completion_tokens!r}, "
            f"total_tokens={self.total_tokens!r}, "
            f"start_date={self.start_date!r}, "
            f"delta_time={self.delta_time!r}, "
            f"final_date={self.final_date!r}, "
            f"input_metadata={self.input_metadata!r}, "
            f"output_metadata={self.output_metadata!r}"
            f")"
        )

    def __iter__(self):
        return iter({
            "content": self.content,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "start_date": self.start_date,
            "delta_time": self.delta_time,
            "final_date": self.final_date,
            "input_metadata": self.input_metadata,
            "output_metadata": self.output_metadata
        }.items())
