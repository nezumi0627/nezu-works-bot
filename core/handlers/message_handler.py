import os

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
from core.handlers.command_handler import DATA_RETRIEVAL_STATE, CommandHandler
from core.logger import RichLogger

logger = RichLogger(__name__)


class PayloadFormatter:
    """ペイロード情報のフォーマットを管理するクラス."""

    @staticmethod
    def format_payload_info(payload: MessagePayload) -> list[str]:
        """ペイロード情報を整形する.

        Args:
            payload: メッセージペイロード

        Returns:
            list[str]: 整形されたペイロード情報のリスト
        """
        payload_info = []

        payload_info.extend(PayloadFormatter._add_notification_type(payload))
        payload_info.extend(PayloadFormatter._add_common_info(payload))

        type_value = int(payload.notification_type)
        payload_info.extend(
            PayloadFormatter._add_type_specific_info(payload, type_value)
        )

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
            PayloadFormatter._add_additional_attrs(payload, excluded_attrs)
        )

        return payload_info

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
        self.ignored_ids = self._load_ignored_ids()

    def _load_ignored_ids(self) -> set[str]:
        """無視するIDをテキストファイルから読み込む。ファイルが存在しない場合は新規作成.

        Returns:
            set[str]: 無視するIDのセット
        """
        ignored_ids_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "ignored_ids.txt",
        )

        # ファイルがない場合は新規作成
        if not os.path.exists(ignored_ids_path):
            logger.info(
                f"{ignored_ids_path} が見つからないため新しく作成します"
            )
            with open(ignored_ids_path, "w", encoding="utf-8") as f:
                f.write(
                    "# 無視するIDのリスト\n"
                )  # コメント行としてファイルに書き込む
            return set()

        try:
            with open(ignored_ids_path, encoding="utf-8") as f:
                return {
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                }
        except FileNotFoundError:
            os.makedirs(os.path.dirname(ignored_ids_path), exist_ok=True)
            with open(ignored_ids_path, "w", encoding="utf-8") as f:
                f.write("# 無視するIDのリスト\n")
            return set()

    def _is_ignored_id(self, user_no: str) -> bool:
        """指定されたIDが無視リストに含まれているかを確認する.

        Args:
            user_no: チェックするユーザーID

        Returns:
            bool: IDが無視リストに含まれている場合はTrue
        """
        return user_no in self.ignored_ids

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
        state = DATA_RETRIEVAL_STATE.get(channel_no)
        if not state:
            return False

        if not state.get("waiting_for_data", False):
            return False
        # 送信者が一致しない場合は処理しない
        if str(state.get("user_no")) != str(payload.user_no) and str(
            state.get("user_no")
        ) != str(payload.from_user_no):
            return False

        # キャンセル処理
        if payload.loc_args1 == "キャンセル":
            state["waiting_for_data"] = False
            works.send_text_message(
                to=channel_no, text="データ取得を中止しました。"
            )
            return True

        # データを保存
        state["data"] = payload

        # 取得したデータの詳細を送信
        works.send_text_message(
            to=payload.channel_no, text=f"[Get Data] Payload:\n{payload!r}"
        )

        # データ取得状態をリセット
        state["waiting_for_data"] = False

        return True

    def handle_message(
        self, works: LineWorks, payload: MessagePayload
    ) -> None:
        """メッセージを処理する.

        Args:
            works: LineWorksクライアント
            payload: メッセージペイロード
        """
        # 無視するIDの場合は処理をスキップ
        if self._is_ignored_id(payload.from_user_no):
            return

        channel_no = payload.channel_no

        if not channel_no:
            return

        if self._handle_data_retrieval(works, payload, channel_no):
            return

        try:
            type_value = int(payload.notification_type)
        except (ValueError, TypeError):
            return

        if type_value == NotificationType.NOTIFICATION_MESSAGE:
            self._handle_text_message(works, payload, channel_no)
        elif type_value == NotificationType.NOTIFICATION_STICKER:
            self._handle_sticker_message(works, payload, channel_no)
        elif type_value == NotificationType.NOTIFICATION_LOCATION:
            self._handle_location_message(works, payload, channel_no)
        elif type_value == 41:
            # 41
            return
        else:
            self._handle_unknown_message(works, payload, channel_no)

    def _handle_text_message(
        self, works: LineWorks, payload: MessagePayload, channel_no: str
    ) -> None:
        """textメッセージを処理する.

        Args:
            works: LineWorks
            payload: MessagePayload
            channel_no: str
        """
        text = payload.loc_args1

        if text in ALL_COMMANDS:
            if text == GET_DATA_COMMAND:
                self.command_map[text](works, channel_no, payload)
            else:
                self.command_map[text](works, channel_no)

    def _handle_sticker_message(
        self, works: LineWorks, payload: MessagePayload, channel_no: str
    ) -> None:
        """stickerメッセージを処理する.

        Args:
            works: LineWorks
            payload: MessagePayload
            channel_no: str
        """
        works.send_text_message(channel_no, f" : {payload.sticker}")
        works.send_sticker_message(channel_no, payload.sticker)

    def _handle_location_message(  # TODO: 位置情報メッセージの処理を実装する
        self, works: LineWorks, payload: MessagePayload, channel_no: str
    ) -> None:
        """locationメッセージを処理する.

        Args:
            works: LineWorks
            payload: MessagePayload
            channel_no: str
        """
        pass

    def _handle_unknown_message(  # TODO: 不明なメッセージの処理を実装する
        self, works: LineWorks, payload: MessagePayload, channel_no: str
    ) -> None:
        """不明なメッセージを処理する.

        Args:
            works: LineWorks
            payload: MessagePayload
            channel_no: str
        """
        pass
