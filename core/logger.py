"""Rich を使用したカスタムロガー.

Author: github.com/nezumi0627
"""

import logging
from typing import Any

from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree


class RichLogger:
    """Richを使用したカスタムロガー."""

    def __init__(self, name: str = __name__) -> None:
        """ロガーの初期化.

        Args:
            name: ロガー名
        """
        # Richコンソールの設定
        self.console = Console()

        # ロガーの設定
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            handlers=[RichHandler(console=self.console)],
        )
        self.logger = logging.getLogger(name)

    def log_info(self, message: str) -> None:
        """情報メッセージを出力.

        Args:
            message: 出力するメッセージ
        """
        self.logger.info(message)

    def log_debug(self, message: str) -> None:
        """デバッグメッセージを出力.

        Args:
            message: 出力するメッセージ
        """
        self.logger.debug(message)

    def log_login(self, works_id: str) -> None:
        """ログイン情報を表示.

        Args:
            works_id: LINE WORKSのID
        """
        panel = Panel(
            f"[bold green]ログイン情報[/bold green]\n\nID: {works_id}",
            title="Login Info",
            border_style="blue",
        )
        self.console.print(panel)

    def log_login_success(
        self, works_id: str, tenant_id: int, domain_id: int, contact_no: int
    ) -> None:
        """ログイン成功情報を表示.

        Args:
            works_id: LINE WORKSのID
            tenant_id: テナントID
            domain_id: ドメインID
            contact_no: コンタクト番号
        """
        table = Table(title="ログイン成功", title_style="bold green")
        table.add_column("項目", style="cyan")
        table.add_column("値", style="yellow")

        table.add_row("Works ID", works_id)
        table.add_row("テナントID", str(tenant_id))
        table.add_row("ドメインID", str(domain_id))
        table.add_row("コンタクトNo.", str(contact_no))

        panel = Panel(table, border_style="blue")
        self.console.print(panel)

    def log_bot_info(self, bot_info: dict[str, dict[str, Any]]) -> None:
        """BOT情報を表示.

        Args:
            bot_info: BOT情報の辞書
        """
        tree = Tree("[bold blue]BOT情報[/bold blue]")

        for category, items in bot_info.items():
            category_tree = tree.add(f"[bold cyan]{category}[/bold cyan]")
            for key, value in items.items():
                if isinstance(value, list):
                    sub_tree = category_tree.add(f"[yellow]{key}:[/yellow]")
                    for item in value:
                        sub_tree.add(str(item))
                else:
                    category_tree.add(f"[yellow]{key}:[/yellow] {value}")

        panel = Panel(tree, title="BOT Info", border_style="blue")
        self.console.print(panel)

    def warning(self, message: str) -> None:
        """警告メッセージを出力.

        Args:
            message: 出力するメッセージ
        """
        self.logger.warning(message)

    def error(self, message: str) -> None:
        """エラーメッセージを出力.

        Args:
            message: 出力するメッセージ
        """
        self.logger.error(message)
