# NezuWorksBot

## 概要

[line-works-sdk](https://github.com/nanato12/line-works-sdk)を使用して作成した、多機能BOTです。

### 使用中のSDKバージョン

- [line-works-sdk v3.4](https://github.com/nanato12/line-works-sdk/releases/tag/v3.4)

## 主な機能や特徴

### 実装済みのコマンドと説明

注意: 接頭辞(PREFIX)はデフォルトで"!"です(変更機能を実装予定)

- `help`: ヘルプメッセージを送信
- `test`: テストメッセージを送信
- `flex`: Flexメッセージを送信
- `getdata`: メッセージまたはコンテンツのデータを取得して表示する

### 技術スタック
- **SDK**: [line-works-sdk v3.4](https://github.com/nanato12/line-works-sdk/releases/tag/v3.4)
- **言語**: Python
- **主要ライブラリ**:
  - `line-works-sdk`
  - `python-dotenv`
  - `rich`

## プロジェクト詳細

### 目的
このBOTは、LINE WORKS向けの多機能BOTです。
SDKの更新に応じて継続的に改良・拡張していきます。

## セットアップ

### 必要な環境
- Python 3.9+
- pip

## セットアップ
1. リポジトリをクローン
2. 必要なパッケージをインストール
```bash
pip install -r requirements.txt
```
3. 環境変数を設定
    - `.env.example`を参考にして、`.env`を書いてください。
4. プロジェクトを実行
```bash
python main.py
```
