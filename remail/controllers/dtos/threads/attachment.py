from dataclasses import dataclass


@dataclass
class AttachmentDTO:
    file_name: str
    file_size: int
    file_type: str
    url: str
