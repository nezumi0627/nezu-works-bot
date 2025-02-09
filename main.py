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

from typing import Any

from line_works.client import LineWorks
from line_works.mqtt.enums.notification_type import NotificationType
from line_works.mqtt.enums.packet_type import PacketType
from line_works.mqtt.models.packet import MQTTPacket
from line_works.tracer import LineWorksTracer

from config.config import PASSWORD, WORKS_ID
from core.bot_info import create_bot_info
from core.handlers.message_handler import MessageHandler
from core.logger import RichLogger

logger = RichLogger(__name__)


class PayloadValidator:
    """ペイロードのバリデーションを管理するクラス."""

    VALID_NOTIFICATION_TYPES = {
        NotificationType.NOTIFICATION_MESSAGE,  # テキストメッセージ
        NotificationType.NOTIFICATION_STICKER,  # スタンプ
        NotificationType.NOTIFICATION_LOCATION,  # 位置情報
    }

    VALID_PAYLOAD_TYPES = {
        "MessagePayload",  # メッセージペイロード
        "StickerPayload",  # スタンプペイロード
        "LocationPayload",  # 位置情報ペイロード
    }

    @classmethod
    def is_valid_notification_type(cls, notification_type: Any) -> bool:
        """通知タイプが有効かどうかを確認する.

        Args:
            notification_type: 確認する通知タイプ

        Returns:
            bool: 通知タイプが有効な場合はTrue
        """
        try:
            type_value = int(notification_type)
            return NotificationType(type_value) in cls.VALID_NOTIFICATION_TYPES
        except (ValueError, TypeError):
            return False

    @classmethod
    def is_valid_payload_type(cls, payload: Any) -> bool:
        """ペイロードの型が有効かどうかを確認する.

        Args:
            payload: 確認するペイロード

        Returns:
            bool: ペイロードの型が有効な場合はTrue
        """
        return payload.__class__.__name__ in cls.VALID_PAYLOAD_TYPES

    @classmethod
    def is_valid_message_payload(cls, payload: Any) -> bool:
        """メッセージペイロードが有効かどうかを確認する.

        Args:
            payload: 確認するペイロード

        Returns:
            bool: メッセージペイロードが有効な場合はTrue
        """
        # ペイロードの型を確認
        if not cls.is_valid_payload_type(payload):
            return False

        # 必要な属性の存在を確認
        if not all(
            hasattr(payload, attr)
            for attr in ["notification_type", "channel_no"]
        ):
            return False

        # 通知タイプを確認
        return cls.is_valid_notification_type(payload.notification_type)


def receive_publish_packet(works: LineWorks, packet: MQTTPacket) -> None:
    """パブリッシュパケットを受信して処理する関数.

    Args:
        works: LineWorksクライアント
        packet: 受信したMQTTパケット
    """
    try:
        if not packet or not hasattr(packet, "payload"):
            logger.warning(
                "Invalid packet received: packet or payload is None"
            )
            return

        payload = packet.payload

        # ペイロードのバリデーション
        if not PayloadValidator.is_valid_message_payload(payload):
            notification_type = getattr(payload, "notification_type", None)
            if notification_type:
                logger.log_info(
                    f"Skipping notification type: {notification_type}"
                )
            else:
                logger.warning(f"Invalid payload type: {type(payload)}")
            return

        if not payload.channel_no:
            logger.warning("No channel number in payload")
            return

        # メッセージハンドラーを作成
        handler = MessageHandler()

        # メッセージを処理
        handler.handle_message(works, payload)

    except Exception as e:
        logger.error(f"Error processing packet: {str(e)}")
        return


def main() -> None:
    """メイン関数."""
    # ログイン情報を表示
    logger.log_login(WORKS_ID)

    # LineWorksクライアントを作成
    works = LineWorks(works_id=WORKS_ID, password=PASSWORD)

    # ログイン成功情報を表示
    logger.log_login_success(
        works_id=WORKS_ID,
        tenant_id=works.tenant_id,
        domain_id=works.domain_id,
        contact_no=works.contact_no,
    )

    # BOT情報を取得して表示
    bot_info = create_bot_info(works.get_my_info())
    logger.log_bot_info(bot_info)

    # トレーサーを作成
    tracer = LineWorksTracer(works=works)

    # パケット受信時のコールバックを設定
    tracer.add_trace_func(PacketType.PUBLISH, receive_publish_packet)

    # トレーサーを開始
    tracer.trace()


if __name__ == "__main__":
    main()
