"""コマンド処理を管理するモジュール."""

from collections.abc import Callable

from line_works.client import LineWorks
from line_works.mqtt.models.payload.message import MessagePayload

from core.constants.commands import (
    ALL_COMMANDS,
    FLEX_COMMAND,
    GET_DATA_COMMAND,
    HELP_COMMAND,
    TEST_COMMAND,
)
from core.utils import load_flex_message


class CommandHandler:
    """コマンド処理を管理するクラス."""

    def __init__(self) -> None:
        """初期化."""
        self.command_map: dict[str, Callable] = {
            HELP_COMMAND: self.help,
            TEST_COMMAND: self.test,
            FLEX_COMMAND: self.flex,
            GET_DATA_COMMAND: self.get_data,
        }

    def handle_command(
        self,
        works: LineWorks,
        channel_no: str,
        text: str,
        payload: MessagePayload,
    ) -> None:
        """コマンドを処理する.

        Args:
            works: LineWorksクライアント
            channel_no: チャンネル番号
            text: 受信したテキスト
            payload: メッセージペイロード
        """
        if text not in ALL_COMMANDS:
            return

        if text == GET_DATA_COMMAND:
            self.command_map[text](works, channel_no, payload)
        else:
            self.command_map[text](works, channel_no)

    @staticmethod
    def help(works: LineWorks, channel_no: str) -> None:
        """ヘルプメッセージを送信.

        Args:
            works: LineWorksクライアント
            channel_no: チャンネル番号
        """
        help_message = load_flex_message("help.json")
        works.send_flex_message(channel_no, flex_content=help_message)

    @staticmethod
    def test(works: LineWorks, channel_no: str) -> None:
        """テストメッセージを送信.

        Args:
            works: LineWorksクライアント
            channel_no: チャンネル番号
        """
        works.send_text_message(channel_no, "I'm work :)")

    @staticmethod
    def flex(works: LineWorks, channel_no: str) -> None:
        """Flexメッセージを送信.

        Args:
            works: LineWorksクライアント
            channel_no: チャンネル番号
        """
        flex_message = load_flex_message("sample.json")
        works.send_flex_message(channel_no, flex_content=flex_message)

    def get_data(
        self,
        works: LineWorks,
        channel_no: str,
        payload: MessagePayload,
    ) -> None:
        """データ取得モードを開始.

        Args:
            works: LineWorksクライアント
            channel_no: チャンネル番号
            payload: メッセージペイロード
        """
        self.data_retrieval_state[channel_no] = {
            "user_no": str(payload.from_user_no),
            "waiting_for_data": True,
            "data": None,
        }
        works.send_text_message(
            channel_no,
            "データを取得したいメッセージやコンテンツを送信してください。",
        )
