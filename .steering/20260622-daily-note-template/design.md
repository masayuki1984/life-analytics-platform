# 技術設計: Daily Note テンプレート対応

**作成日**: 2026-06-22

---

## アーキテクチャ概要

変更は `obsidian_writer.py` と `plaud_importer.py` の 2 ファイルに集中する。
`config.py` / `plaud_client.py` は変更なし。

```
plaud_importer.main()
  ├─ writer.ensure_daily_note(target_date)
  │     └─ _ensure_daily_note(d)
  │           ├─ path.exists() → 何もしない（既存保護）
  │           └─ 新規作成
  │                 ├─ Templates/daily.md が存在 → write_text でコピー
  │                 └─ 存在しない → touch（WARNING ログ）
  │
  ├─ [録音 0 件の場合]
  │     writer.write_no_recordings(target_date)
  │           ├─ _ensure_daily_note(d)  ← 冪等（既に存在する）
  │           ├─ _is_no_recordings_written() → True なら何もしない
  │           ├─ _ensure_plaud_section()
  │           └─ append "録音なし"
  │
  └─ [録音がある場合]（既存フロー）
        for rec in recordings:
          writer.process_recording(rec, summary, target_date)
```

## ディレクトリ・ファイル構成

変更ファイルのみ記載（新規ファイルなし）。

```
life_analytics/
├── obsidian_writer.py   # _ensure_daily_note 修正 + write_no_recordings 追加
└── plaud_importer.py    # 録音 0 件時に write_no_recordings を呼ぶ

tests/
└── test_obsidian_writer.py  # テンプレート・録音なし系テスト追加

docs/specs/plaud-importer.md  # Daily Note 生成仕様を更新
README.md                     # Templates/daily.md の記載を追加
```

## 主要クラス・関数設計

### `ObsidianWriter._ensure_daily_note`（修正後）

```python
def _ensure_daily_note(self, d: date) -> Path:
    path = self._daily_note_path(d)
    if not path.exists():
        template_path = self.vault_path / "Templates" / "daily.md"
        use_template = template_path.exists()
        if self.dry_run:
            src = "テンプレート使用" if use_template else "空ファイル"
            logger.info(f"[DRY-RUN] Daily Note を作成します ({src}): {path}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            if use_template:
                content = template_path.read_text(encoding="utf-8")
                path.write_text(content, encoding="utf-8")
                logger.info(f"[created] Daily Note を作成しました (テンプレート使用): {path.name}")
            else:
                path.touch()
                logger.warning(
                    f"Templates/daily.md が見つかりません。空ファイルで作成しました: {path.name}"
                )
    return path
```

**変更点:**
- `template_path = vault_path / "Templates" / "daily.md"` の存在を確認
- 存在すれば `write_text` でコピー、なければ `touch`（既存挙動） + WARNING

### `ObsidianWriter.write_no_recordings`（新規）

```python
def write_no_recordings(self, d: date) -> None:
    """録音がない日に Daily Note の Plaud セクションへ '録音なし' を書き込む（冪等）。"""
    daily_path = self._ensure_daily_note(d)

    if not self.dry_run and self._is_no_recordings_written(daily_path):
        logger.debug(f"[skip] '録音なし' は既に記録済みです: {daily_path.name}")
        return

    self._ensure_plaud_section(daily_path)

    if self.dry_run:
        logger.info(f"[DRY-RUN] Daily Note に '録音なし' を追記します: {daily_path.name}")
    else:
        with open(daily_path, "a", encoding="utf-8") as f:
            f.write("\n録音なし\n")
        logger.info(f"[created] '録音なし' を追記しました: {daily_path.name}")
```

### `ObsidianWriter._is_no_recordings_written`（新規）

```python
def _is_no_recordings_written(self, note_path: Path) -> bool:
    """'録音なし' が既に書き込まれているか確認する。"""
    if not note_path.exists():
        return False
    return "録音なし" in note_path.read_text(encoding="utf-8")
```

### `plaud_importer.main`（修正後・抜粋）

```python
writer.ensure_daily_note(target_date)

if not recordings:
    writer.write_no_recordings(target_date)

for rec in recordings:
    ...
```

## データスキーマ

### テンプレートファイル

| 項目 | 値 |
|---|---|
| パス | `{vault_path}/Templates/daily.md` |
| フォーマット | Markdown（変数展開なし） |
| 必須 | No（なければ空ファイルにフォールバック） |

### `## Plaud` セクションの書き込み内容

| ケース | 書き込み内容 |
|---|---|
| 録音あり（standalone） | `- [[Notes/PLAUD/…\|name]] — duration` + `<!-- plaud:{id} -->` |
| 録音あり（IDEA_） | `### 💡 name` + `<!-- plaud:{id} -->` + 要約 |
| 録音なし | `録音なし` |

## 依存関係

- 既存モジュール: `life_analytics/obsidian_writer.py`, `life_analytics/plaud_importer.py`
- 外部ライブラリ: 追加なし（`pathlib` は標準ライブラリ）

## 技術的判断・トレードオフ

| 判断 | 採用案 | 却下案 | 理由 |
|---|---|---|---|
| テンプレートパス | `vault_path / "Templates" / "daily.md"` 固定 | 環境変数で設定可能 | 要件がハードコードを指定。変更が必要になったときに Config に追加すればよい |
| テンプレート変数展開 | 行わない | `{{date}}` を置換 | Obsidian の「テンプレート」プラグインが担う責務。CLI が変換すると二重管理になる |
| `録音なし` の重複チェック | ファイル全体で `録音なし` を検索 | Plaud セクション内のみ | MVP として十分。Daily Note に `録音なし` が他の文脈で現れる可能性は極めて低い |
| dry-run でのテンプレート存在チェック | 実ファイルを読んで判定する | 常に「テンプレートあり」と仮定 | ログの正確性を保つため実チェックを行う（書き込みは行わない） |

## 懸念事項・リスク

- `Templates/daily.md` が存在しない環境では WARNING が毎日出力される。初回セットアップ時に案内が必要
- テンプレート内容が大きい場合のメモリ使用量は問題にならない（Markdown ファイルは数 KB 程度）
