# 技術設計: [フィーチャー名]

**作成日**: YYYY-MM-DD

---

## アーキテクチャ概要

<!-- データフロー・モジュール構成を図または箇条書きで説明 -->

```
[入力] → [処理モジュール] → [出力/保存]
```

## ディレクトリ・ファイル構成

```
{SRC_DIR}/
└── [新規ディレクトリ]/
    ├── [file1]     # 役割説明
    └── [file2]     # 役割説明
```

## 主要クラス・関数設計

### `ClassName`

```python
class ClassName:
    def method_name(self, arg: Type) -> ReturnType:
        """簡潔な説明"""
        ...
```

## データスキーマ

### 入力

```
# 例: 入力データの構造
{
    "field1": type,   # 説明
    "field2": type,
    "field3": type
}
```

### 出力 / 保存フォーマット

- **形式**: {FORMAT}  <!-- ex: JSON / CSV / Parquet -->
- **保存先**: {STORAGE_PATH}  <!-- ex: s3://bucket/path, ./output/, DBテーブル名 -->

## 依存関係

- 既存モジュール: `{SRC_DIR}/{module_path}`  <!-- ex: src/utils/logger.py -->
- 外部ライブラリ: {libraries}  <!-- ex: requests, pydantic -->

## 技術的判断・トレードオフ

<!-- なぜこの設計を選んだか、代替案と比較して -->

## 懸念事項・リスク

- 