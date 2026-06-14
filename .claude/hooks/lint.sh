#!/usr/bin/env bash
# PostToolUse hook: Edit / Write のたびに自動実行される Lint スクリプト
#
# 【カスタマイズ方法】
# プロジェクトの言語・ツールに合わせて以下のいずれかのブロックを有効化し、
# 他は削除またはコメントアウトしてください。
#
# 終了コード:
#   0     — OK（Claude Code の処理を続行）
#   非 0  — エラー（Claude Code にエラー内容を返し、修正を促す）
# ---------------------------------------------------------------

# ---- Python (Ruff) ----
# ruff check . --fix --quiet
# ruff format . --quiet

# ---- TypeScript / JavaScript (ESLint + Prettier) ----
# npx eslint --fix "$(jq -r '.tool_input.file_path' < /dev/stdin)" --quiet
# npx prettier --write "$(jq -r '.tool_input.file_path' < /dev/stdin)"

# ---- Go ----
# gofmt -w .
# go vet ./...

# ---- Ruby (RuboCop) ----
# bundle exec rubocop --autocorrect --format quiet

# ---------------------------------------------------------------
# デフォルト: 何もせず正常終了（Lint 未設定のプロジェクト向け）
exit 0
