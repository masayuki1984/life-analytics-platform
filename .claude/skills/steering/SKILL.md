# Steering スキル

セッション別の作業ドキュメント（`.steering/`）を管理し、計画・実装・振り返りを一貫して追跡するスキル。

---

## 動作モード

このスキルは呼び出し方によって 3 つのモードで動作する。

---

## モード 1: 計画（Planning）

**呼び出し**: `Skill(steering)` を `planning` モードで呼ぶ、またはフィーチャー名を渡す

### 手順

1. `.steering/[YYYYMMDD]-[フィーチャー名]/` ディレクトリを作成する
   - 日付は今日の日付（`currentDate` から取得）
   - フィーチャー名は英小文字・ハイフン区切り（例: `historical-data-collection`）
2. 以下の 3 ファイルをテンプレートから生成する:
   - `requirements.md` — 要件定義
   - `design.md` — 技術設計
   - `tasklist.md` — タスクリスト（チェックボックス付き）
3. 各ファイルについてユーザーに確認を取り、承認されたら次のファイルへ進む
4. **1 ファイルずつ作成・確認する。一度に全部作らない**

### テンプレート参照

- `.claude/skills/steering/templates/requirements.md`
- `.claude/skills/steering/templates/design.md`
- `.claude/skills/steering/templates/tasklist.md`

---

## モード 2: 実装（Implementation）

**呼び出し**: `.steering/[date]-[feature]/tasklist.md` が存在する状態で呼ぶ

### 手順

1. `tasklist.md` を読み込み、未完了（`[ ]`）のタスクを特定する
2. 最初の未完了タスクから順番に実装する
3. **各タスク完了直後に `tasklist.md` を更新して `[x]` にマークする**（バッチ更新禁止）
4. 全タスクが `[x]` になるまでループする
5. タスクをスキップする場合は技術的な理由を `tasklist.md` にコメントとして記録する

### 重要ルール

- タスクは必ず上から順番に処理する
- 1 タスク完了 → 即 `tasklist.md` 更新 → 次のタスクへ
- 実装中に新たなサブタスクが発生した場合は `tasklist.md` に追記してから取り組む
- ユーザー確認なしに実装を進める（確認が必要な場合のみ停止）

---

## モード 3: 振り返り（Retrospective）

**呼び出し**: 全タスク完了後

### 手順

1. `tasklist.md` の `## 振り返り` セクションに以下を記録する:
   - 予想外だったこと・詰まったポイント
   - 次回に活かせる学び
   - 残タスク・技術的負債（あれば）
2. 簡潔に 3〜5 箇条書きでまとめる

---

## ステアリングディレクトリの命名規則

```
.steering/
└── YYYYMMDD-feature-name/
    ├── requirements.md
    ├── design.md
    └── tasklist.md
```

例:
- `.steering/20260423-historical-data-collection/`
- `.steering/20260430-backtest-engine/`