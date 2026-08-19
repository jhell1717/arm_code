from dataclasses import dataclass, field

@dataclass(frozen=True)
class Task:
    name: str
    dependencies: list[str] = field(default_factory=list)

ExecutionStage = list[str]
