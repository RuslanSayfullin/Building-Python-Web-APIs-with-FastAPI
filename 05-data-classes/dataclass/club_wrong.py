from dataclasses import dataclass

# tag::CLUBMEMBER[]
@dataclass
class ClubMember:
    """этот класс возбуждает исключение ValueError"""
    name: str
    guests: list = []
# end::CLUBMEMBER[]
