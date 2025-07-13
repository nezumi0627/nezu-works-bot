"""GitHub Actions 用の自動アップデートスクリプト。

1. LINE WORKS SDK を最新バージョンにアップグレード
2. インストールした SDK のバージョンを README.md に反映

このスクリプトは idempotent です。
README.md に変更がなかった場合は、終了コード0で何も行いません。
"""

from __future__ import annotations

import datetime
import json
import logging
import pathlib
import re
import subprocess
import sys
import urllib.request
from typing import Final

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

REPO_ROOT: Final[pathlib.Path] = pathlib.Path(__file__).resolve().parent.parent
README_PATH: Final[pathlib.Path] = REPO_ROOT / "README.md"
SDK_PACKAGE_NAME: Final[str] = "line-works-sdk"
VERSION_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"SDK バージョン: (?P<ver>[0-9]+\.[0-9]+\.[0-9]+)"
)


def get_installed_version() -> str | None:
    """現在インストールされている SDK のバージョンを取得。未インストールなら None。"""
    try:
        import importlib.metadata as importlib_metadata  # Python 3.8+
    except ImportError:  # pragma: no cover
        import importlib_metadata  # type: ignore

    try:
        return importlib_metadata.version(SDK_PACKAGE_NAME)
    except importlib_metadata.PackageNotFoundError:  # type: ignore[attr-defined]
        return None


def get_latest_version() -> str:
    """PyPI の JSON API から最新バージョンを取得。"""
    url = f"https://pypi.org/pypi/{SDK_PACKAGE_NAME}/json"
    with urllib.request.urlopen(url, timeout=10) as resp:
        data = json.load(resp)
    return data["info"]["version"]


def upgrade_sdk_if_needed() -> str:
    """最新バージョンを確認し、必要ならアップグレードして新バージョンを返す。"""
    installed = get_installed_version()
    latest = get_latest_version()

    if installed == latest:
        logger.info(
            "SDK は最新です (installed=%s, latest=%s).", installed, latest
        )
        return installed or latest

    logger.info("SDK をアップグレードします: %s -> %s", installed, latest)
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            f"{SDK_PACKAGE_NAME}=={latest}",
        ]
    )
    return latest


def update_readme(sdk_version: str) -> bool:
    """README.md に SDK バージョンおよび更新日時を反映。

    Args:
        sdk_version: インストールされている SDK のバージョン。

    Returns:
        変更が発生した場合は True、それ以外は False。
    """
    if not README_PATH.exists():
        logger.warning("README.md が見つかりません。スキップします。")
        return False

    content = README_PATH.read_text(encoding="utf-8")
    updated = content

    lines = updated.splitlines()

    # SDK バージョンセクションを検索
    header_idx = None
    for i, ln in enumerate(lines):
        if ln.strip() == "## SDK バージョン":
            header_idx = i
            break

    version_line = f"現在の LINE WORKS SDK バージョン: {sdk_version}"

    if header_idx is not None:
        # セクションが存在する場合、次行を差し替え
        if header_idx + 1 < len(lines):
            lines[header_idx + 1] = version_line
        else:
            lines.insert(header_idx + 1, version_line)
    else:
        # セクションが無い場合、ファイル冒頭の大見出し直後に追加
        insert_pos = 0
        for i, ln in enumerate(lines):
            if ln.startswith("#"):
                insert_pos = i + 1
                break
        lines[insert_pos:insert_pos] = [
            "",
            "## SDK バージョン",
            version_line,
            "",
        ]

    updated = "\n".join(lines)

    # 更新日時の反映
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    if "最終更新:" in updated:
        updated = re.sub(r"最終更新: .*", f"最終更新: {timestamp}", updated)
    else:
        updated += f"\n\n最終更新: {timestamp}\n"

    if updated != content:
        README_PATH.write_text(updated, encoding="utf-8")
        logger.info("README.md を更新しました。")
        return True

    logger.info("README.md に変更はありません。")
    return False


def main() -> None:
    """CLI エントリーポイント。デフォルトは `--all`。"""
    import argparse

    parser = argparse.ArgumentParser(
        description="LINE WORKS SDK & README Updater"
    )
    parser.add_argument(
        "--sdk",
        action="store_true",
        help="SDK のみアップグレード",
    )
    parser.add_argument(
        "--readme",
        action="store_true",
        help="README のみ更新",
    )

    args = parser.parse_args()

    # フラグ未指定なら両方実行 (--all)
    mode_sdk = args.sdk or not (args.sdk or args.readme)
    mode_readme = args.readme or not (args.sdk or args.readme)

    exit_code = 0

    if mode_sdk:
        sdk_version = upgrade_sdk_if_needed()
    else:
        # SDK は変化しないため現在バージョンを取得
        sdk_version = get_installed_version() or "unknown"

    if mode_readme:
        changed = update_readme(sdk_version)
        exit_code = 1 if changed else 0

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
