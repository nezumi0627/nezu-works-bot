"""メッセージ処理を管理するモジュール."""

from line_works.client import LineWorks
from line_works.mqtt.enums.notification_type import NotificationType
from line_works.mqtt.models.payload.message import MessagePayload

from core.constants.commands import (
    ALL_COMMANDS,
    FLEX_COMMAND,
    GET_DATA_COMMAND,
    HELP_COMMAND,
    TEST_COMMAND,
)
from core.logger import RichLogger
from core.utils import load_flex_message

logger = RichLogger(__name__)

# データ取得状態を管理する辞書
DATA_RETRIEVAL_STATE: dict[str, dict[str, str | None]] = {}


class CommandHandler:
    """コマンド処理を管理するクラス."""

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


class PayloadFormatter:
    """ペイロード情報のフォーマットを管理するクラス."""

    @staticmethod
    def _add_notification_type(payload: MessagePayload) -> list[str]:
        """通知タイプ情報を追加する.

        Args:
            payload: メッセージペイロード

        Returns:
            list[str]: 通知タイプ情報のリスト
        """
        return [f"NotificationType: {payload.notification_type}"]

    @staticmethod
    def _add_type_specific_info(
        payload: MessagePayload, type_value: int
    ) -> list[str]:
        """メッセージタイプ固有の情報を追加する.

        Args:
            payload: メッセージペイロード
            type_value: 通知タイプの数値

        Returns:
            list[str]: メッセージタイプ固有の情報のリスト
        """
        info = []
        if type_value == NotificationType.NOTIFICATION_MESSAGE:
            info.append(f"Message: {payload.loc_args1}")
        elif type_value == NotificationType.NOTIFICATION_STICKER:
            info.append(f"Sticker: {payload.sticker}")
        elif type_value == NotificationType.NOTIFICATION_LOCATION:
            info.append(f"Location: {payload.location}")
        return info

    @staticmethod
    def _add_common_info(payload: MessagePayload) -> list[str]:
        """共通情報を追加する.

        Args:
            payload: メッセージペイロード

        Returns:
            list[str]: 共通情報のリスト
        """
        return [
            f"From User: {payload.from_user_no}",
            f"Channel: {payload.channel_no}",
            f"Create Time: {payload.create_time}",
        ]

    @staticmethod
    def _add_additional_attrs(
        payload: MessagePayload, excluded_attrs: set[str]
    ) -> list[str]:
        """追加の属性情報を追加する.

        Args:
            payload: メッセージペイロード
            excluded_attrs: 除外する属性のセット

        Returns:
            list[str]: 追加の属性情報のリスト
        """
        info = []
        for attr in dir(payload):
            if not attr.startswith("_") and attr not in excluded_attrs:
                value = getattr(payload, attr)
                if value is not None and value != "":
                    info.append(f"{attr}: {value}")
        return info

    @staticmethod
    def format_payload_info(payload: MessagePayload) -> list[str]:
        """ペイロード情報を整形する.

        Args:
            payload: メッセージペイロード

        Returns:
            list[str]: 整形されたペイロード情報のリスト
        """
        payload_info = PayloadFormatter._add_notification_type(payload)

        try:
            type_value = int(payload.notification_type)
            type_specific_info = PayloadFormatter._add_type_specific_info(
                payload, type_value
            )
            if type_specific_info:
                payload_info.extend(type_specific_info)
                payload_info.extend(PayloadFormatter._add_common_info(payload))

                excluded_attrs = {
                    "notification_type",
                    "loc_args1",
                    "sticker",
                    "location",
                    "from_user_no",
                    "channel_no",
                    "create_time",
                }
                payload_info.extend(
                    PayloadFormatter._add_additional_attrs(
                        payload, excluded_attrs
                    )
                )
        except (ValueError, TypeError):
            pass

        return payload_info


class MessageHandler:
    """メッセージ処理を管理するクラス."""

    def __init__(self) -> None:
        """初期化."""
        self.command_handler = CommandHandler()
        self.command_map = {
            HELP_COMMAND: self.command_handler.help,
            TEST_COMMAND: self.command_handler.test,
            FLEX_COMMAND: self.command_handler.flex,
            GET_DATA_COMMAND: self.command_handler.get_data,
        }
        self.payload_formatter = PayloadFormatter()

    def _handle_data_retrieval(
        self, works: LineWorks, payload: MessagePayload, channel_no: str
    ) -> bool:
        """データ取得状態の処理を行う.

        Args:
            works: LineWorksクライアント
            payload: メッセージペイロード
            channel_no: チャンネル番号

        Returns:
            bool: データ取得状態の処理を行った場合はTrue
        """
        if not (
            channel_no in DATA_RETRIEVAL_STATE
            and DATA_RETRIEVAL_STATE[channel_no].get("waiting_for_data", False)
            and str(payload.from_user_no)
            == DATA_RETRIEVAL_STATE[channel_no]["user_no"]
        ):
            return False

        # データを保存
        DATA_RETRIEVAL_STATE[channel_no]["data"] = str(payload)
        DATA_RETRIEVAL_STATE[channel_no]["waiting_for_data"] = False

        # ペイロード情報を整形して送信
        payload_info = self.payload_formatter.format_payload_info(payload)
        works.send_text_message(
            channel_no, "[Get Data]\n" + "\n".join(payload_info)
        )
        return True

    def _handle_text_message(
        self, works: LineWorks, payload: MessagePayload, channel_no: str
    ) -> None:
        """テキストメッセージの処理を行う.

        Args:
            works: LineWorksクライアント
            payload: メッセージペイロード
            channel_no: チャンネル番号
        """
        text = payload.loc_args1

        # データ取得モードの処理を優先
        if (
            channel_no in DATA_RETRIEVAL_STATE
            and DATA_RETRIEVAL_STATE[channel_no]["waiting_for_data"]
        ):
            DATA_RETRIEVAL_STATE[channel_no]["data"] = text
            works.send_text_message(
                channel_no, f"データを取得しました: {text}"
            )
            DATA_RETRIEVAL_STATE[channel_no]["waiting_for_data"] = False
            return

        if text not in ALL_COMMANDS:
            return

        if text == GET_DATA_COMMAND:
            self.command_map[text](works, channel_no, payload)
        else:
            self.command_map[text](works, channel_no)

    def _handle_sticker_message(
        self, works: LineWorks, payload: MessagePayload, channel_no: str
    ) -> None:
        """スタンプメッセージの処理を行う.

        Args:
            works: LineWorksクライアント
            payload: メッセージペイロード
            channel_no: チャンネル番号
        """
        works.send_text_message(channel_no, f"スタンプ情報: {payload.sticker}")
        works.send_sticker_message(channel_no, payload.sticker)

    def _handle_location_message(
        self, works: LineWorks, payload: MessagePayload, channel_no: str
    ) -> None:
        """位置情報メッセージの処理を行う.

        Args:
            works: LineWorksクライアント
            payload: メッセージペイロード
            channel_no: チャンネル番号
        """
        works.send_text_message(channel_no, f"位置情報: {payload.location}")

    def _handle_unknown_message(
        self, works: LineWorks, payload: MessagePayload, channel_no: str
    ) -> None:
        """未知のメッセージタイプの処理を行う.

        Args:
            works: LineWorksクライアント
            payload: メッセージペイロード
            channel_no: チャンネル番号
        """
        # ペイロード情報を整形して送信
        payload_info = self.payload_formatter.format_payload_info(payload)
        works.send_text_message(
            channel_no,
            f"未知のメッセージタイプ: {payload.notification_type}\n"
            + "\n".join(payload_info),
        )

    def handle_message(
        self, works: LineWorks, payload: MessagePayload
    ) -> None:
        """メッセージを処理する.

        Args:
            works: LineWorksクライアント
            payload: メッセージペイロード
        """
        # チャンネル番号がない場合は処理しない
        if not payload.channel_no:
            return

        # 受信メッセージのログ出力
        logger.log_info(f"受信メッセージ: {payload!r}")

        channel_no = payload.channel_no

        # データ取得状態の処理
        if self._handle_data_retrieval(works, payload, channel_no):
            return

        try:
            type_value = int(payload.notification_type)
        except (ValueError, TypeError):
            logger.warning(
                f"Invalid notification type: {payload.notification_type}"
            )
            return

        # メッセージタイプごとの処理
        if type_value == NotificationType.NOTIFICATION_MESSAGE:
            self._handle_text_message(works, payload, channel_no)
        elif type_value == NotificationType.NOTIFICATION_STICKER:
            self._handle_sticker_message(works, payload, channel_no)
        elif type_value == NotificationType.NOTIFICATION_LOCATION:
            self._handle_location_message(works, payload, channel_no)
        else:
            # マッピングされていない通知タイプの処理
            self._handle_unknown_message(works, payload, channel_no)
