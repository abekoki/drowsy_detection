#!/usr/bin/env python3
"""
GitHub Actions用情報表示スクリプト
コミット情報を整形して表示・ファイル保存
Windows CMD環境でのUnicode対応
"""

import base64
import os
import sys
from datetime import datetime


def safe_print(text: str):
    """安全な文字列出力（Unicode対応）"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Unicodeエラーの場合はASCII文字に置換
        safe_text = text.encode('ascii', 'replace').decode('ascii')
        print(safe_text)


def decode_commit_message(encoded_message: str) -> str:
    """Base64エンコードされたコミットメッセージをデコード"""
    try:
        return base64.b64decode(encoded_message).decode('utf-8')
    except Exception:
        return encoded_message  # デコードに失敗した場合は元の文字列を返す


def decode_changelog(encoded_changelog: str) -> str:
    """Base64エンコードされたchangelogをデコード"""
    try:
        return base64.b64decode(encoded_changelog).decode('utf-8')
    except Exception:
        return encoded_changelog  # デコードに失敗した場合は元の文字列を返す


def display_info():
    """情報を表示"""
    # GitHub Actionsの出力から情報を取得
    commit_hash = os.environ.get('COMMIT_HASH', 'unknown')
    commit_short = os.environ.get('COMMIT_SHORT', 'unknown')
    commit_message_b64 = os.environ.get('COMMIT_MESSAGE_B64', '')
    commit_date = os.environ.get('COMMIT_DATE', 'unknown')
    branch_name = os.environ.get('BRANCH_NAME', 'unknown')
    version = os.environ.get('VERSION', 'unknown')
    changelog_b64 = os.environ.get('CHANGELOG_B64', '')
    
    # コミットメッセージとchangelogをデコード
    commit_message = decode_commit_message(commit_message_b64)
    changelog = decode_changelog(changelog_b64)
    
    # 現在時刻を取得
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S JST')
    
    safe_print("==========================================")
    safe_print("[INFO] プロジェクト情報")
    safe_print("==========================================")
    safe_print(f"[VER] バージョン: {version}")
    safe_print(f"[BR] ブランチ: {branch_name}")
    safe_print(f"[TIME] 実行日時: {current_time}")
    safe_print("")
    safe_print("==========================================")
    safe_print("[COMMIT] コミット情報")
    safe_print("==========================================")
    safe_print(f"[HASH] コミットハッシュ: {commit_hash}")
    safe_print(f"[SHORT] 短縮ハッシュ: {commit_short}")
    safe_print(f"[MSG] コミットメッセージ: {commit_message}")
    safe_print(f"[DATE] コミット日時: {commit_date}")
    safe_print("")
    safe_print("==========================================")
    safe_print("[CHANGELOG] 変更ログ（直近5コミット）")
    safe_print("==========================================")
    safe_print(changelog)
    safe_print("")
    safe_print("==========================================")
    safe_print("[OK] 情報表示完了")
    safe_print("==========================================")


def save_to_file():
    """情報をファイルに保存"""
    # GitHub Actionsの出力から情報を取得
    commit_hash = os.environ.get('COMMIT_HASH', 'unknown')
    commit_short = os.environ.get('COMMIT_SHORT', 'unknown')
    commit_message_b64 = os.environ.get('COMMIT_MESSAGE_B64', '')
    commit_date = os.environ.get('COMMIT_DATE', 'unknown')
    branch_name = os.environ.get('BRANCH_NAME', 'unknown')
    version = os.environ.get('VERSION', 'unknown')
    changelog_b64 = os.environ.get('CHANGELOG_B64', '')
    
    # コミットメッセージとchangelogをデコード
    commit_message = decode_commit_message(commit_message_b64)
    changelog = decode_changelog(changelog_b64)
    
    # 現在時刻を取得
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S JST')
    
    # ファイルに保存（UTF-8エンコーディング）
    try:
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
        
        safe_print("[SAVE] 情報を commit_info.txt に保存しました")
        
        # ファイル内容を表示
        with open('commit_info.txt', 'r', encoding='utf-8') as f:
            content = f.read()
            safe_print(content)
            
    except Exception as e:
        safe_print(f"[ERROR] ファイル保存エラー: {e}")


def main():
    """メイン処理"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'save':
        save_to_file()
    else:
        display_info()


if __name__ == "__main__":
    main()
