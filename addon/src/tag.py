from dataclasses import dataclass


@dataclass
class Tag:
    """A class representing a tag."""

    name: str
    shortcut: str
