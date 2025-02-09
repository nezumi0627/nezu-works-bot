"""ユーティリティ関数を提供するモジュール."""

import json
from pathlib import Path

from line_works.requests.send_message import FlexContent


def load_flex_message(filename: str) -> FlexContent:
    """Flexメッセージのテンプレートを読み込む.

    Args:
        filename: 読み込むJSONファイルの名前

    Returns:
        読み込んだFlexメッセージの内容
    """
    flex_dir = Path(__file__).parent.parent / "flex_messages"
    with open(flex_dir / filename, encoding="utf-8") as f:
        content = json.load(f)
    return FlexContent(alt_text="Flex Message", contents=content)
