# GitHub Actions セルフホストランナー設定ガイド

## 概要

このプロジェクトでは、GitHub Actionsでセルフホストランナーを使用してコミット情報を表示するワークフローを実行します。

## セルフホストランナーの設定手順

### 1. GitHubリポジトリでの設定

1. GitHubリポジトリの **Settings** → **Actions** → **Runners** に移動
2. **New self-hosted runner** をクリック
3. ランナーのOSを選択（Windows/Linux/macOS）
4. 表示されるコマンドを実行環境で実行

### 2. Python環境の事前インストール

セルフホストランナー環境にPython 3.10以上を事前にインストールしてください：

#### Windows環境でのインストール

```powershell
# Python 3.10のダウンロード（公式サイトから）
# https://www.python.org/downloads/release/python-31011/

# または、Chocolateyを使用（推奨）
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Python 3.10をインストール
choco install python --version=3.10.11 -y

# インストール確認
python --version
python -c "import tomllib; print('tomllib利用可能')"
```

#### Linux環境でのインストール

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-dev

# CentOS/RHEL
sudo yum install python3.10 python3.10-pip

# インストール確認
python3.10 --version
python3.10 -c "import tomllib; print('tomllib利用可能')"
```

### 3. Windows環境での設定

```powershell
# ランナー用ディレクトリを作成
mkdir actions-runner
cd actions-runner

# ランナーをダウンロード（GitHubから提供されるURLを使用）
Invoke-WebRequest -Uri "https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-win-x64-2.311.0.zip" -OutFile "actions-runner-win-x64-2.311.0.zip"

# 解凍
Expand-Archive -Path "actions-runner-win-x64-2.311.0.zip" -DestinationPath .

# 設定
.\config.cmd --url https://github.com/[ユーザー名]/[リポジトリ名] --token [トークン]

# ランナーをサービスとしてインストール（オプション）
.\install.cmd
```

### 3. ランナーの起動

```powershell
# 手動起動
.\run.cmd

# サービスとして起動（install.cmd実行後）
net start "GitHub Actions Runner ([リポジトリ名])"
```

## ワークフローの動作

### トリガー条件
- **push** イベント（全ブランチ）

### 実行内容
1. **コードチェックアウト**: 全履歴を取得
2. **Python環境セットアップ**: Python 3.10
3. **情報取得**:
   - コミットハッシュ（完全版・短縮版）
   - コミットメッセージ
   - コミット日時
   - ブランチ名
   - バージョン（pyproject.tomlから）
   - 変更ログ（直近5コミット）
4. **情報表示**: コンソールに整形して表示
5. **ファイル保存**: commit_info.txtに保存
6. **アーティファクト保存**: GitHubに30日間保存

### 出力例

```
==========================================
📋 プロジェクト情報
==========================================
🏷️  バージョン: 0.1.1
🌿 ブランチ: main
📅 実行日時: 2025-10-07 13:15:30 JST

==========================================
🔗 コミット情報
==========================================
📝 コミットハッシュ: fa5172b1234567890abcdef...
🔖 短縮ハッシュ: fa5172b
💬 コミットメッセージ: 仕様書、設計書、パッケージのバージョンをv0.1.1に統一更新
⏰ コミット日時: 2025-08-26 13:10:55 +0900

==========================================
📜 変更ログ（直近5コミット）
==========================================
fa5172b 仕様書、設計書、パッケージのバージョンをv0.1.1に統一更新...
3bfa566 config: 眠気検知パラメータのチューニング
e3803bb .gitignoreにpytestのキャッシュディレクトリを追加...
32c925d プロジェクトのパッケージ化に向けた準備を行い...
6bc2eb9 全てのソースコードファイルとテスト結果ファイルを削除...

==========================================
✅ 情報表示完了
==========================================
```

## 🚨 緊急対応: PowerShell実行ポリシーエラー

### 問題
```
Error: File ... cannot be loaded because running scripts is disabled on this system
```

### 即座の解決方法

#### 1. システム管理者による緊急修正（最優先）

**管理者権限でPowerShellを開いて実行**:
```powershell
# 現在の実行ポリシーを確認
Get-ExecutionPolicy -List

# システム全体の実行ポリシーを変更（緊急対応）
Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope LocalMachine -Force

# ユーザーレベルでも変更
Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope CurrentUser -Force

# 変更確認
Get-ExecutionPolicy -List
```

#### 2. ワークフローの変更（PowerShell回避）

現在のワークフローは`shell: cmd`を使用してPowerShellを完全に回避しています。

#### 3. セルフホストランナー環境の確認

```powershell
# ランナーが正常に動作するか確認
cd C:\actions-runner
.\run.cmd --check
```

## トラブルシューティング

### よくある問題

1. **PowerShell実行ポリシーエラー**
   ```
   Error: ./setup.ps1 : File ... cannot be loaded because running scripts is disabled on this system
   ```
   
   **解決方法**:
   ```powershell
   # 現在の実行ポリシーを確認
   Get-ExecutionPolicy
   
   # 実行ポリシーを変更（管理者権限が必要）
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine
   
   # または、より安全な設定
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **ランナーが認識されない**
   - GitHubリポジトリのSettingsでランナーが登録されているか確認
   - ランナーが起動しているか確認

3. **Pythonバージョンエラー**
   - セルフホストランナー環境にPython 3.10以上がインストールされているか確認

4. **権限エラー**
   - ランナーがリポジトリにアクセス権限を持っているか確認

### ログ確認

GitHub Actionsの実行ログは以下で確認できます：
- リポジトリの **Actions** タブ
- 該当ワークフローの実行履歴をクリック

## カスタマイズ

### 表示するコミット数を変更

`.github/workflows/display-info.yml`の以下の行を変更：
```yaml
CHANGELOG=$(git log --oneline -5)  # 5を変更
```

### 追加情報の表示

`Get commit information`ステップに以下を追加：
```yaml
# 追加の情報を取得
ADDITIONAL_INFO=$(git diff --stat HEAD~1)
echo "additional_info<<EOF" >> $GITHUB_OUTPUT
echo "$ADDITIONAL_INFO" >> $GITHUB_OUTPUT
echo "EOF" >> $GITHUB_OUTPUT
```

## 注意事項

- セルフホストランナーは常時起動している必要があります
- ランナーのリソース使用量に注意してください
- セキュリティ上、信頼できる環境でのみ使用してください
