from dataclasses import dataclass


@dataclass
class SenderDTO:
    id: int | None
    first_name: str
    last_name: str
    email: str
