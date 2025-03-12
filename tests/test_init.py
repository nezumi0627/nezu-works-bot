from src.nezu_works_bot import hello


def test_hello() -> None:
    assert hello() == "Hello from nezu-works-bot!"
