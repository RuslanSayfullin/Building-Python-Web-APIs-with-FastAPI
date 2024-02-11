from dataclasses import dataclass, field

@dataclass
class ClubMember:
    """это определение ClubMember более точное"""
    name: str
    guests: list[str] = field(default_factory=list)  # <1>
