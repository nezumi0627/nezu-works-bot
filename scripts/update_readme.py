"""README.md をテンプレートから生成するスクリプト。

`templates/README.template.md` を読み込み、`{{VAR}}` プレースホルダを
指定値で置換してプロジェクトルートの `README.md` を上書きする。
"""

from __future__ import annotations

import datetime
import logging
import pathlib
import re
from typing import Dict, Final

from auto_update import get_installed_version  # type: ignore

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


TEMPLATES: Final[dict[pathlib.Path, pathlib.Path]] = {
    pathlib.Path(__file__).resolve().parent.parent
    / "templates/README.template.md": pathlib.Path(__file__)
    .resolve()
    .parent.parent
    / "README.md",
    pathlib.Path(__file__).resolve().parent.parent
    / "templates/README-en.template.md": pathlib.Path(__file__)
    .resolve()
    .parent.parent
    / "README-en.md",
}
PLACEHOLDER_PATTERN: Final[re.Pattern[str]] = re.compile(r"{{([A-Z0-9_]+)}}")


def render_template(
    template_path: pathlib.Path, vars_map: Dict[str, str]
) -> str:
    """テンプレートを読み込み、変数置換後の文字列を返す。"""
    text = template_path.read_text(encoding="utf-8")

    def repl(match: re.Match[str]) -> str:  # pragma: no cover
        key = match.group(1)
        return vars_map.get(key, match.group(0))

    return PLACEHOLDER_PATTERN.sub(repl, text)


def main() -> None:  # noqa: D401
    """エントリーポイント."""
    vars_map: Dict[str, str] = {
        "SDK_VERSION": get_installed_version() or "unknown",
        "LAST_UPDATED": datetime.datetime.utcnow().strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        ),
        # 以下は例として 0 をセット
        # メトリクス取得処理を追加する場合はここを書き換える
        "ERROR_COUNT": "0",
        "TOTAL_MESSAGES": "0",
        "TOTAL_COMMANDS": "0",
        "COMMAND_USAGE_RATE": "0%",
        "COMMAND_TEST": "0",
        "COMMAND_MSG": "0",
        "COMMAND_FLEX": "0",
        "COMMAND_STICKER": "0",
        "COMMAND_HELP": "0",
    }

    for template_path, output_path in TEMPLATES.items():
        rendered = render_template(template_path, vars_map)

        if (
            output_path.exists()
            and output_path.read_text(encoding="utf-8") == rendered
        ):
            logger.info("%s に変更はありません。", output_path.name)
            continue

        output_path.write_text(rendered, encoding="utf-8")
        logger.info("%s を更新しました。", output_path.name)


if __name__ == "__main__":
    main()
