# -*- coding: utf-8 -*-
"""GitHub Actions 失敗通知スクリプト

GitHub Actions の `workflow_run` イベントでジョブが失敗した際に実行し、
LINE WORKS へテキストメッセージを送信する

必要な環境変数:
    WORKS_ID: ボットの LINE WORKS ID
    WORKS_PASSWORD: ボットのパスワード
    WORKS_CHANNEL_NO: 通知先チャンネル番号

GitHub が自動で設定する環境変数も利用して失敗情報を整形する
"""

from __future__ import annotations

import datetime
import logging
import os
import pathlib
import sys
from typing import Final

from line_works.client import LineWorks
from line_works.openapi.talk.models.flex_content import FlexContent

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ---------- 環境変数ロード ----------


def _load_local_env() -> None:
    """ローカル実行時に .env を読み込んで os.environ を補完"""
    if os.getenv("GITHUB_ACTIONS"):
        return

    env_path = pathlib.Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k, v.strip().strip("\"'"))


_load_local_env()

# ---------- 設定 ----------
WORKS_ID: Final[str | None] = os.getenv("WORKS_ID")
WORKS_PASSWORD: Final[str | None] = os.getenv("WORKS_PASSWORD")
_channel_no_raw = os.getenv("WORKS_CHANNEL_NO")
CHANNEL_NO: Final[int | None]
try:
    CHANNEL_NO = int(_channel_no_raw) if _channel_no_raw else None
except ValueError:
    logger.error(
        "WORKS_CHANNEL_NO は整数である必要があります: %s", _channel_no_raw
    )
    sys.exit(1)

if not WORKS_ID or not WORKS_PASSWORD or not CHANNEL_NO:
    logger.error(
        "環境変数が不足しています\n"
        "(WORKS_ID=%s, WORKS_PASSWORD=%s, WORKS_CHANNEL_NO=%s)",
        bool(WORKS_ID),
        bool(WORKS_PASSWORD),
        bool(CHANNEL_NO),
    )
    sys.exit(1)


# ---------- メッセージ生成 ----------
def build_flex_content() -> FlexContent:
    """失敗詳細を含む FlexContent を生成"""
    repo = os.getenv("GITHUB_REPOSITORY", "unknown")
    workflow = os.getenv("GITHUB_WORKFLOW", "unknown")
    run_id = os.getenv("GITHUB_RUN_ID", "0")
    attempt = os.getenv("GITHUB_RUN_ATTEMPT", "1")
    sha = os.getenv("GITHUB_SHA", "")[:7]
    server_url = os.getenv("GITHUB_SERVER_URL", "https://github.com")
    run_url = f"{server_url}/{repo}/actions/runs/{run_id}"
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    contents = {
        "type": "bubble",
        "size": "mega",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {
                    "type": "text",
                    "text": "🚨 GitHub Actions Failure",
                    "weight": "bold",
                    "color": "#D9534F",
                    "wrap": True,
                    "size": "md",
                },
                {"type": "text", "text": f"Repo: {repo}", "wrap": True},
                {
                    "type": "text",
                    "text": f"Workflow: {workflow}",
                    "wrap": True,
                },
                {
                    "type": "text",
                    "text": f"Run: {run_id} (attempt {attempt})",
                    "wrap": True,
                },
                {"type": "text", "text": f"Commit: {sha}", "wrap": True},
                {"type": "text", "text": f"Time: {timestamp}", "wrap": True},
                {
                    "type": "button",
                    "style": "link",
                    "action": {
                        "type": "uri",
                        "label": "View Run",
                        "uri": run_url,
                    },
                },
            ],
        },
    }

    return FlexContent(alt_text="GitHub Actions Failure", contents=contents)


def main() -> None:
    """エントリーポイント"""
    works = LineWorks(works_id=WORKS_ID, password=WORKS_PASSWORD)

    flex = build_flex_content()
    logger.info("Send Flex Failure message")

    try:
        works.send_flex_message(CHANNEL_NO, flex_content=flex)
    except Exception as exc:
        logger.exception("LINE WORKS への送信に失敗しました: %s", exc)
        sys.exit(1)

    logger.info("通知を送信しました")


if __name__ == "__main__":
    main()
