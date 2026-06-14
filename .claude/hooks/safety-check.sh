#!/usr/bin/env bash
# PreToolUse hook: Bash コマンド実行前に安全性を確認するスクリプト
#
# stdin から実行予定のコマンドを JSON で受け取る:
#   { "tool_name": "Bash", "tool_input": { "command": "..." } }
#
# 終了コード:
#   0     — OK（コマンドの実行を許可）
#   非 0  — ブロック（コマンドの実行を停止し、理由を Claude Code に返す）
# ---------------------------------------------------------------

COMMAND=$(jq -r '.tool_input.command // ""' < /dev/stdin)

# ---- 危険なコマンドパターンをブロック ----
BLOCKED_PATTERNS=(
  "rm -rf /"
  "rm -rf \*"
  "chmod -R 777 /"
  "> /etc/"
  "dd if=/dev/zero"
)

for pattern in "${BLOCKED_PATTERNS[@]}"; do
  if echo "$COMMAND" | grep -qF "$pattern"; then
    echo "BLOCKED: 危険なコマンドパターンを検出しました: $pattern"
    exit 1
  fi
done

# ---- プロジェクト固有のブロックルールをここに追加 ----
# 例: 本番 DB への直接書き込みをブロック
# if echo "$COMMAND" | grep -qE "psql.*prod"; then
#   echo "BLOCKED: 本番 DB への直接操作は禁止されています"
#   exit 1
# fi

# ---- 例: .env ファイルの cat / print をブロック ----
# if echo "$COMMAND" | grep -qE "(cat|print|echo).*\.env"; then
#   echo "BLOCKED: .env ファイルの内容出力は禁止されています"
#   exit 1
# fi

exit 0
