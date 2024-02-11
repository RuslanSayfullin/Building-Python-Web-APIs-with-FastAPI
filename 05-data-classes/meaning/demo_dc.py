from dataclasses import dataclass

@dataclass
class DemoDataClass:
    """класс с декоратором @dataclass"""
    a: int           # <1>
    b: float = 1.1   # <2>
    c = 'spam'       # <3>
