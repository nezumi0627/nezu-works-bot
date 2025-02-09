"""ボット情報の構造を定義するモジュール.

Author: github.com/nezumi0627
"""

from typing import Any


def create_bot_info(my_info: Any) -> dict[str, dict[str, Any]]:
    """ボット情報を構造化して返す.

    Args:
        my_info: LINE WORKSから取得したボット情報

    Returns:
        構造化されたボット情報
    """
    return {
        "基本情報": {
            "名前": my_info.name.display_name,
            "組織": my_info.organization,
            "役職": my_info.position or "未設定",
            "部署": my_info.department or "未設定",
            "場所": my_info.location or "未設定",
        },
        "システム情報": {
            "テナントID": my_info.tenant_id,
            "ドメインID": my_info.domain_id,
            "コンタクト番号": my_info.contact_no,
            "インスタンス": my_info.instance,
        },
        "連絡先": {
            "メール": [
                f"{e.content} ({e.type_code}{'※' if e.represent else ''})"
                for e in my_info.emails
            ],
            "SNS": [
                f"{m['protocol']}: {m['content']}" for m in my_info.messengers
            ],
        },
        "アカウント設定": {
            "読み取り専用": my_info.read_only,
            "一時ID": my_info.temp_id,
            "アクセス制限": my_info.access_limit,
            "写真変更可能": my_info.user_photo_modify,
            "不在設定可能": my_info.user_absence_modify,
        },
        "Works連携": {
            "招待URL": my_info.works_at.invite_url,
            "ユーザー検索ブロック": my_info.works_at.id_search_block,
            "利用可能サービス": my_info.works_services,
            "接続ユーザー": [
                (f"{user.service_type}: {user.name} "
                 f"(ID: {user.id}, No: {user.works_at_user_no})")
                for user in my_info.works_at.users
            ],
        },
    }
