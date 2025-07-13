# nezu-works-bot

## SDK バージョン
現在の LINE WORKS SDK バージョン: {{SDK_VERSION}}

こんにちは！私は**ねずわーくす**です :)

このリポジトリはテスト目的でのみ使用されており、実際に完成版としての利用を目的としていません。

## 統計情報

* **エラー数**: {{ERROR_COUNT}}
* **受信したメッセージの総数**: {{TOTAL_MESSAGES}}
* **使用されたコマンドの総数**: {{TOTAL_COMMANDS}}
* **コマンド使用率**: {{COMMAND_USAGE_RATE}}

### コマンド使用グラフ
```mermaid
%%{init: {'themeVariables': {'pie1': '#e67e73', 'pie2': '#8e44ad', 'pie3': '#2ecc71', 'pie4': '#3498db', 'pie5': '#f1c40f', 'pieTitleText': '#ffffff'}}}%%
pie
    title コマンド使用状況
    "test": {{COMMAND_TEST}}
    "/msg": {{COMMAND_MSG}}
    "/flex": {{COMMAND_FLEX}}
    "/sticker": {{COMMAND_STICKER}}
    "/help": {{COMMAND_HELP}}
```

### ライセンス
[MITライセンス](LICENSE)

最終更新: {{LAST_UPDATED}}
