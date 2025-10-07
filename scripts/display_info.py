#!/usr/bin/env python3
"""
GitHub Actions用情報表示スクリプト
コミット情報を整形して表示・ファイル保存
"""

import base64
import os
from datetime import datetime


def decode_commit_message(encoded_message: str) -> str:
    """Base64エンコードされたコミットメッセージをデコード"""
    try:
        return base64.b64decode(encoded_message).decode('utf-8')
    except Exception:
        return encoded_message  # デコードに失敗した場合は元の文字列を返す


def display_info():
    """情報を表示"""
    # GitHub Actionsの出力から情報を取得
    commit_hash = os.environ.get('COMMIT_HASH', 'unknown')
    commit_short = os.environ.get('COMMIT_SHORT', 'unknown')
    commit_message_b64 = os.environ.get('COMMIT_MESSAGE_B64', '')
    commit_date = os.environ.get('COMMIT_DATE', 'unknown')
    branch_name = os.environ.get('BRANCH_NAME', 'unknown')
    version = os.environ.get('VERSION', 'unknown')
    changelog = os.environ.get('CHANGELOG', '')
    
    # コミットメッセージをデコード
    commit_message = decode_commit_message(commit_message_b64)
    
    # 現在時刻を取得
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S JST')
    
    print("==========================================")
    print("📋 プロジェクト情報")
    print("==========================================")
    print(f"🏷️  バージョン: {version}")
    print(f"🌿 ブランチ: {branch_name}")
    print(f"📅 実行日時: {current_time}")
    print()
    print("==========================================")
    print("🔗 コミット情報")
    print("==========================================")
    print(f"📝 コミットハッシュ: {commit_hash}")
    print(f"🔖 短縮ハッシュ: {commit_short}")
    print(f"💬 コミットメッセージ: {commit_message}")
    print(f"⏰ コミット日時: {commit_date}")
    print()
    print("==========================================")
    print("📜 変更ログ（直近5コミット）")
    print("==========================================")
    print(changelog)
    print()
    print("==========================================")
    print("✅ 情報表示完了")
    print("==========================================")


def save_to_file():
    """情報をファイルに保存"""
    # GitHub Actionsの出力から情報を取得
    commit_hash = os.environ.get('COMMIT_HASH', 'unknown')
    commit_short = os.environ.get('COMMIT_SHORT', 'unknown')
    commit_message_b64 = os.environ.get('COMMIT_MESSAGE_B64', '')
    commit_date = os.environ.get('COMMIT_DATE', 'unknown')
    branch_name = os.environ.get('BRANCH_NAME', 'unknown')
    version = os.environ.get('VERSION', 'unknown')
    changelog = os.environ.get('CHANGELOG', '')
    
    # コミットメッセージをデコード
    commit_message = decode_commit_message(commit_message_b64)
    
    # 現在時刻を取得
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S JST')
    
    # ファイルに保存
    with open('commit_info.txt', 'w', encoding='utf-8') as f:
        f.write("プロジェクト情報\n")
        f.write("================\n")
        f.write(f"バージョン: {version}\n")
        f.write(f"ブランチ: {branch_name}\n")
        f.write(f"実行日時: {current_time}\n")
        f.write("\n")
        f.write("コミット情報\n")
        f.write("============\n")
        f.write(f"コミットハッシュ: {commit_hash}\n")
        f.write(f"短縮ハッシュ: {commit_short}\n")
        f.write(f"コミットメッセージ: {commit_message}\n")
        f.write(f"コミット日時: {commit_date}\n")
        f.write("\n")
        f.write("変更ログ（直近5コミット）\n")
        f.write("========================\n")
        f.write(f"{changelog}\n")
    
    print("📄 情報を commit_info.txt に保存しました")
    
    # ファイル内容を表示
    with open('commit_info.txt', 'r', encoding='utf-8') as f:
        print(f.read())


def main():
    """メイン処理"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'save':
        save_to_file()
    else:
        display_info()


if __name__ == "__main__":
    main()
