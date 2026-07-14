from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class Job:
    id: int
    payload: str
    created: datetime = field(default_factory=datetime.utcnow)
