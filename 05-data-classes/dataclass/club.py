from dataclasses import dataclass, field

@dataclass
class ClubMember:
    """это определение ClubMember работает"""
    name: str
    guests: list = field(default_factory=list)

