import os
import sys

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from src.nezu_works_bot import hello


@pytest.mark.parametrize("input_", [None])
def test_hello(input_: str | None) -> None:
    """Tests that the message is as expected."""
    expected = (
        "Hello from nezu-works-bot! "
        "I'm a bot that can be used to automate tasks on GitHub."
    )
    assert hello(input_) == expected, (  # noqa: S101
        f"Expected {expected!r} but got {hello(input_)!r}"
    )
