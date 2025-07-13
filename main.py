# -*- coding: utf-8 -*-
import json
import logging
import os

from line_works.client import LineWorks
from line_works.mqtt.enums.notification_type import NotificationType
from line_works.mqtt.enums.packet_type import PacketType
from line_works.mqtt.exceptions import PacketParseException
from line_works.mqtt.models.packet import MQTTPacket
from line_works.mqtt.models.payload.message import MessagePayload
from line_works.openapi.talk.models.flex_content import FlexContent
from line_works.tracer import LineWorksTracer

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    works_id = os.getenv("WORKS_ID")
    password = os.getenv("WORKS_PASSWORD")

    works = LineWorks(works_id=works_id, password=password)

    my_info = works.get_my_info()
    logger.info("my_info=%s", my_info)

    def receive_publish_packet(w: LineWorks, p: MQTTPacket) -> None:
        try:
            payload = p.payload
        except PacketParseException as exc:
            logger.warning("Skip packet: %s", exc)
            return

        if not isinstance(payload, MessagePayload):
            return

        if not payload.channel_no:
            return

        logger.info("payload=%s", payload)

        if payload.loc_args1 == "test":
            w.send_text_message(payload.channel_no, "ok")

        elif payload.loc_args1 == "/msg":
            w.send_text_message(payload.channel_no, f"{payload!r}")

        elif payload.loc_args1 == "/flex":
            with open("src/sample_flex.json") as f:
                j: dict = json.load(f)
            w.send_flex_message(
                payload.channel_no,
                flex_content=FlexContent(alt_text="test", contents=j),
            )

        if payload.notification_type == NotificationType.NOTIFICATION_STICKER:
            w.send_text_message(payload.channel_no, " ")
            w.send_text_message(payload.channel_no, f"{payload.sticker=}")

            w.send_sticker_message(payload.channel_no, payload.sticker)

    tracer = LineWorksTracer(works=works)
    tracer.add_trace_func(PacketType.PUBLISH, receive_publish_packet)
    tracer.trace()


if __name__ == "__main__":
    main()
