"""環境変数の設定モジュール.

Author: github.com/nezumi0627
"""

import os

from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

WORKS_ID: str = os.getenv("WORKS_ID", "")
PASSWORD: str = os.getenv("WORKS_PASSWORD", "")
