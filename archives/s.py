"""NezuWorksBot @nezumi0627.

Author: github.com/nezumi0627

Description:
This BOT is created using line-works-sdk and will be updated or changed based
on the sdk update.

This BOT is not intended to promote or encourage any violation of the rules
of the LINE WORKS platform.

Using sdk Link(line-works-sdk v3.4):
https://github.com/nanato12/line-works-sdk/releases/tag/v3.4
"""

from line_works.client import LineWorks
from line_works.mqtt.enums.notification_type import NotificationType
from line_works.mqtt.enums.packet_type import PacketType
from line_works.mqtt.models.packet import MQTTPacket
from line_works.mqtt.models.payload.message import MessagePayload
from line_works.tracer import LineWorksTracer

from config.config import PASSWORD, WORKS_ID
from core.bot_info import create_bot_info
from core.logger import RichLogger
from core.utils import load_flex_message

logger = RichLogger(__name__)

# データ取得状態を管理する辞書
DATA_RETRIEVAL_STATE: dict[str, dict[str, str | None]] = {}


class CommandHandler:
    """コマンド処理のためのクラス."""

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

    @classmethod
    def get_data(
        cls, works: LineWorks, channel_no: str, payload: MessagePayload
    ) -> None:
        """データ取得モードを開始.

        Args:
            works: LineWorksクライアント
            channel_no: チャンネル番号
            payload: メッセージペイロード
        """
        global DATA_RETRIEVAL_STATE

        DATA_RETRIEVAL_STATE[channel_no] = {
            "user_no": str(payload.from_user_no),
            "waiting_for_data": True,
            "data": None,
        }
        works.send_text_message(
            channel_no,
            "データを取得したいメッセージやコンテンツを送信してください。",
        )


def handle_text_command(
    works: LineWorks, channel_no: str, text: str, payload: MessagePayload
) -> None:
    """テキストメッセージを処理する関数.

    Args:
        works: LineWorksクライアント
        channel_no: チャンネル番号
        text: 受信したテキスト
        payload: メッセージペイロード
    """
    command_map = {
        "!help": CommandHandler.help,
        "!test": CommandHandler.test,
        "!flex": CommandHandler.flex,
        "!getdata": CommandHandler.get_data,
    }

    # コマンドの処理
    if text in command_map:
        if text == "!getdata":
            command_map[text](works, channel_no, payload)
        else:
            command_map[text](works, channel_no)


def handle_sticker(
    works: LineWorks, channel_no: str, payload: MessagePayload
) -> None:
    """スタンプメッセージを処理する関数.

    Args:
        works: LineWorksクライアント
        channel_no: チャンネル番号
        payload: メッセージペイロード
    """
    if payload.notification_type == NotificationType.NOTIFICATION_STICKER:
        works.send_text_message(channel_no, f"スタンプ情報: {payload.sticker}")
        works.send_sticker_message(channel_no, payload.sticker)


def handle_payload(works: LineWorks, payload: MessagePayload) -> None:
    """ペイロードタイプに応じた処理を行う関数.

    Args:
        works: LineWorksクライアント
        payload: 受信したペイロード
    """
    global DATA_RETRIEVAL_STATE

    # チャンネル番号がない場合は処理しない
    if not payload.channel_no:
        return

    # 受信メッセージのログ出力
    logger.log_info(f"受信メッセージ: {payload!r}")

    # データ取得状態のチェック
    if (
        payload.channel_no in DATA_RETRIEVAL_STATE
        and DATA_RETRIEVAL_STATE[payload.channel_no].get(
            "waiting_for_data", False
        )
        and str(payload.from_user_no)
        == DATA_RETRIEVAL_STATE[payload.channel_no]["user_no"]
    ):
        # データを保存
        DATA_RETRIEVAL_STATE[payload.channel_no]["data"] = str(payload)
        DATA_RETRIEVAL_STATE[payload.channel_no]["waiting_for_data"] = False

        # payloadを丸ごと表示
        works.send_text_message(
            payload.channel_no,
            f"[Get Data] Payload:\n{payload!r}",
        )
        return

    # テキストコマンドの処理
    if payload.loc_args1:
        handle_text_command(
            works, payload.channel_no, payload.loc_args1, payload
        )

    # スタンプの処理
    handle_sticker(works, payload.channel_no, payload)


def receive_publish_packet(works: LineWorks, packet: MQTTPacket) -> None:
    """パブリッシュパケットを受信して処理する関数.

    Args:
        works: LineWorksクライアント
        packet: 受信したMQTTパケット
    """
    payload = packet.payload

    # MessagePayload以外は処理しない
    if not isinstance(payload, MessagePayload):
        return

    # ペイロードの処理
    handle_payload(works, payload)


def main() -> None:
    """メイン関数."""
    # ログイン情報を表示
    logger.log_login(WORKS_ID)

    works = LineWorks(works_id=WORKS_ID, password=PASSWORD)

    # 自身の情報を取得して表示
    my_info = works.get_my_info()
    logger.log_bot_info(create_bot_info(my_info))

    # トレーサーの設定
    tracer = LineWorksTracer(works=works)
    tracer.add_trace_func(PacketType.PUBLISH, receive_publish_packet)
    tracer.trace()


if __name__ == "__main__":
    main()
