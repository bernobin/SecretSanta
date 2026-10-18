from secret_santa_bot.messages import get_welcome_message


def test_get_welcome_message() -> None:
    assert get_welcome_message() == "Welcome to Secret Santa! 🎅"
