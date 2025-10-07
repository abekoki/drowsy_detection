#!/usr/bin/env python3
"""
GitHub Actions用コミット情報取得スクリプト
セルフホストランナー環境でのPowerShell実行ポリシー問題を回避
"""

import subprocess
import tomllib
import base64
import json
import sys
from pathlib import Path


def run_git_command(command: str) -> str:
    """Gitコマンドを実行して結果を取得"""
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Gitコマンドエラー: {e}", file=sys.stderr)
        return ""


def get_commit_info():
    """コミット情報を取得"""
    info = {}
    
    # コミットハッシュ
    info['commit_hash'] = run_git_command('git rev-parse HEAD')
    info['commit_short'] = run_git_command('git rev-parse --short HEAD')
    
    # コミットメッセージ
    commit_message = run_git_command('git log -1 --pretty=format:"%s"')
    info['commit_message'] = commit_message
    info['commit_message_b64'] = base64.b64encode(commit_message.encode('utf-8')).decode('ascii')
    
    # コミット日時
    info['commit_date'] = run_git_command('git log -1 --pretty=format:"%ci"')
    
    # ブランチ名
    info['branch_name'] = run_git_command('git rev-parse --abbrev-ref HEAD')
    
    # バージョン情報（pyproject.tomlから）
    try:
        with open('pyproject.toml', 'rb') as f:
            data = tomllib.load(f)
            info['version'] = data['project']['version']
    except Exception as e:
        print(f"バージョン取得エラー: {e}", file=sys.stderr)
        info['version'] = "unknown"
    
    # 変更ログ（直近5コミット）
    changelog = run_git_command('git log --oneline -5')
    info['changelog'] = changelog
    info['changelog_b64'] = base64.b64encode(changelog.encode('utf-8')).decode('ascii')
    
    return info


def write_github_output(info: dict):
    """GitHub Actionsの出力に設定"""
    github_output_path = os.environ.get('GITHUB_OUTPUT')
    
    if github_output_path:
        try:
            with open(github_output_path, 'a', encoding='utf-8') as f:
                # 安全な出力のみ（Base64エンコードされたもの）
                safe_outputs = [
                    'commit_hash', 'commit_short', 'commit_message_b64', 
                    'commit_date', 'branch_name', 'version', 'changelog_b64'
                ]
                for key in safe_outputs:
                    if key in info:
                        f.write(f"{key}={info[key]}\n")
        except Exception as e:
            print(f"GitHub出力ファイル書き込みエラー: {e}", file=sys.stderr)
    else:
        # GitHub Actions環境でない場合は、環境変数として設定
        for key, value in info.items():
            print(f"export {key}={value}")


def main():
    """メイン処理"""
    try:
        # コミット情報を取得
        info = get_commit_info()
        
        # GitHub Actionsの出力に設定
        write_github_output(info)
        
        # コンソールにも表示
        print("=== コミット情報取得完了 ===")
        for key, value in info.items():
            if key == 'commit_message_b64':
                continue  # Base64は表示しない
            print(f"{key}: {value}")
        
        return 0
        
    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    import os
    sys.exit(main())
