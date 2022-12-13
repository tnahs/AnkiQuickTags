import pytest

from addon.src.tag import Tag


@pytest.fixture(scope="session")
def tags() -> list[Tag]:
    return [
        Tag(name="Tag01", shortcut="Ctrl+1"),
        Tag(name="Tag02", shortcut="Ctrl+2"),
        Tag(name="Tag03", shortcut="Ctrl+3"),
    ]
