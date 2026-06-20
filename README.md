# life-analytics-platform

Plaud CLI から録音要約を取得し、Obsidian SecondBrain へ自動インポートするツール。

---

## セットアップ

### 前提

- Python 3.11+
- [uv](https://github.com/astral-sh/uv)
- Node.js / npx（Plaud CLI 実行用）

### インストール

```bash
# 依存関係のインストール
uv sync --extra dev

# Plaud CLI の認証（初回のみ）
npx @plaud-ai/cli login
```

ブラウザが開き、Plaud アカウントでログインすると認証トークンが保存される。
self-hosted runner など GUI がない環境では、別のマシンで `plaud login` を実行し、
生成されたトークンファイル（`~/.plaud/`）をコピーする。

### 環境変数の設定

```bash
cp .env.example .env
```

`.env` を編集して以下を設定する:

```bash
# Obsidian Vault の絶対パス（必須）
OBSIDIAN_VAULT_PATH=/Users/masayuki_kato/Obsidian/SecondBrain

# Plaud CLI コマンド（任意）
# PLAUD_CLI=npx @plaud-ai/cli

# CLI タイムアウト秒数（任意 — デフォルト: 60）
# PLAUD_TIMEOUT=60

# ログレベル（任意）
# LOG_LEVEL=INFO
```

---

## 使い方

### 手動実行

```bash
# 昨日分の録音をインポート
uv run python -m life_analytics.plaud_importer

# 特定の日付を指定してインポート
uv run python -m life_analytics.plaud_importer --date 2026-06-14

# ファイルを書き込まずに処理内容を確認（dry-run）
uv run python -m life_analytics.plaud_importer --dry-run
uv run python -m life_analytics.plaud_importer --date 2026-06-14 --dry-run
```

### cron 設定例（毎日 00:30 に前日分を処理）

```crontab
30 0 * * * cd /path/to/life-analytics-platform && uv run python -m life_analytics.plaud_importer >> /tmp/plaud-importer.log 2>&1
```

または launchd（macOS）:

```xml
<!-- ~/Library/LaunchAgents/com.local.plaud-importer.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.local.plaud-importer</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/life-analytics-platform/.venv/bin/python</string>
        <string>-m</string>
        <string>life_analytics.plaud_importer</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/path/to/life-analytics-platform</string>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>0</integer>
        <key>Minute</key>
        <integer>30</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/tmp/plaud-importer.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/plaud-importer.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>OBSIDIAN_VAULT_PATH</key>
        <string>/Users/yourname/SecondBrain</string>
    </dict>
</dict>
</plist>
```

---

## トラブルシューティング

### 認証トークン切れ（`AUTH_FAILED`）

自動実行時に以下のエラーが出た場合、Plaud CLI の認証トークンが期限切れになっている。

```
ERROR: Plaud CLI の認証が期限切れです。`plaud login` を実行してください。
ERROR: 復旧手順: `plaud login` を実行して再認証してください。
```

**復旧手順:**

Mac mini 環境では通常、以下のコマンドで再認証できる。

```bash
npx @plaud-ai/cli login
```

ブラウザが起動できないサーバー環境の場合のみ、別のマシンで再ログインしてから
`tokens.json` をコピーする方法を検討してください。

```bash
# 1. ブラウザが使える開発機で再ログインする
npx @plaud-ai/cli login

# 2. 生成されたトークンファイルをサーバーへコピーする
scp ~/.plaud/tokens.json gha-runner@mac-mini:~/.plaud/tokens.json

# 3. サーバー側で動作確認する
npx @plaud-ai/cli recent --days 1
```

### タイムアウト

ネットワークが不安定な環境では `PLAUD_TIMEOUT` を延ばす（デフォルト 60 秒）。

```bash
# .env に追記
PLAUD_TIMEOUT=120
```

---

## タイトルプレフィックスによるルーティング

録音後に Plaud アプリでタイトルにプレフィックスを付けることで保存先を制御する。

| プレフィックス | 保存先 |
|---|---|
| `IDEA_` | Daily Note の `## Plaud` セクションに直接追記 |
| `MEETING_` | `Notes/PLAUD/{date}-{name}.md` に単独ノート作成 + Daily Note にリンク |
| `SEMINAR_` | 同上 |
| `STUDY_` | 同上 |
| プレフィックスなし | 同上 |

---

## 開発

```bash
# テスト実行
uv run pytest -v

# Lint / Format チェック
uv run ruff check .
uv run ruff format --check .

# 自動修正
uv run ruff check --fix .
uv run ruff format .
```

---

## Obsidian Vault 構成（前提）

```
SecondBrain/
├── Daily/
│   └── YYYY/
│       └── MM/
│           └── YYYY-MM-DD.md    ← Daily Note
├── Notes/
│   └── PLAUD/
│       └── YYYY-MM-DD-{name}.md ← 単独ノート
└── ...
```
