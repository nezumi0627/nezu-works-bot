"""LINE WORKS SDK を最新バージョンへアップグレードするスクリプト。

GitHub Actions やローカルで実行し、必要な場合のみアップグレードを行います。
終了コードは常に 0 です。
"""

from __future__ import annotations

import logging

from auto_update import upgrade_sdk_if_needed  # type: ignore

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def main() -> None:  # noqa: D401
    """CLI エントリーポイント."""
    version = upgrade_sdk_if_needed()
    logger.info("SDK 更新完了 (current=%s)", version)


if __name__ == "__main__":
    main()
