<!-- TEMPLATE: /setup-project を実行するか直接編集して、{PLACEHOLDER} を実際の値に書き換えてください。 -->
<!-- 記入後に <!-- ex: --> コメントと、このブロックを削除してください。 -->

# アーキテクチャ設計

**最終更新**: {YYYY-MM-DD}
**ステータス**: 確定 | 草案 | 見直し中 | 廃止

---

## 全体構成

<!-- レイヤー数・名称はプロジェクトに合わせて変更する。 -->
<!--
ex（トレーディング）: Data Collection → Strategy → Execution → Risk Management → Backtest → Monitoring
ex（Web アプリ）: Presentation → Application → Domain → Infrastructure
-->

```
┌─────────────────────────────────────────────────┐
│  Layer 1: {LAYER_1_NAME}                        │
│  {LAYER_1_DIR}/（{STATUS}）                     │
│  - {RESPONSIBILITY_1}                           │
│  - {RESPONSIBILITY_2}                           │
└─────────────┬───────────────────────────────────┘
              │ {DATA_BETWEEN_1_AND_2}
┌─────────────▼───────────────────────────────────┐
│  Layer 2: {LAYER_2_NAME}                        │
│  {LAYER_2_DIR}/（{STATUS}）                     │
│  - {RESPONSIBILITY_1}                           │
│  - {RESPONSIBILITY_2}                           │
└─────────────┬───────────────────────────────────┘
              │ {DATA_BETWEEN_2_AND_3}
┌─────────────▼───────────────────────────────────┐
│  Layer 3: {LAYER_3_NAME}                        │
│  {LAYER_3_DIR}/（{STATUS}）                     │
│  - {RESPONSIBILITY_1}                           │
└─────────────────────────────────────────────────┘
```

---

## 実装フェーズとレイヤーの対応

| フェーズ | レイヤー | 状態 |
|---|---|---|
| フェーズ 1 | {LAYER_1_NAME} | {STATUS} |
| フェーズ 2 | {LAYER_2_NAME} | {STATUS} |
| フェーズ 3 | {LAYER_3_NAME} | **{STATUS}** |

---

## ディレクトリ構造と各モジュールの役割

<!--
ex（Python）:
Application/
├── API/
│   ├── public_api.py       # PublicAPI 統一インターフェース（抽象クラス）
│   └── private_api.py      # PrivateAPI 統一インターフェース（抽象クラス）
├── AppUtility/
│   ├── log.py              # ロガー（全モジュール共通）
│   └── exceptions.py       # 例外定義
└── Client/
    └── initializer.py      # エントリポイント
-->

```
{SRC_DIR}/
├── {MODULE_1}/
│   ├── {file_1}.{EXT}    # {ROLE}
│   └── {file_2}.{EXT}    # {ROLE}
├── {MODULE_2}/
│   └── {file_3}.{EXT}    # {ROLE}
└── {MODULE_3}/
    └── {file_4}.{EXT}    # {ROLE}
```

---

## 技術スタック

<!--
ex（Python）:
| カテゴリ | 既存 | 新規モジュール採用候補 |
|---|---|---|
| 依存管理 | Pipenv | **uv**（段階移行） |
| データ処理 | pandas | **Polars**（10-100x 高速） |
| Lint/Format | — | **Ruff** |
-->

| カテゴリ | 既存 | 新規モジュール採用候補 |
|---|---|---|
| 言語 | {LANGUAGE} {VERSION} | 同左 |
| 依存管理 | {PACKAGE_MANAGER} | {NEW_PACKAGE_MANAGER} |
| {CATEGORY} | {CURRENT_TOOL} | **{NEW_TOOL}**（{REASON}） |

---

## ストレージ・データ設計

<!-- ファイルパス規約・DB スキーマ・データフォーマット等を記載する。不要なら削除する。 -->

### パス規約 / 保存先

```
{STORAGE_PATH_PATTERN}
```
<!-- ex（S3）: s3://{bucket}/{exchange}/{symbol}/{timeframe}/{YYYY}/{MM}/{DD}.parquet -->
<!-- ex（ローカル）: ./data/{category}/{YYYY}/{MM}/{DD}.csv -->
<!-- ex（DB）: テーブル名 `{schema}.{table}` -->

### 主要データスキーマ

<!--
ex（OHLCV）:
| カラム | 型 | 制約 |
|---|---|---|
| timestamp | int64 | UTC Unix ミリ秒、単調増加 |
| open | float64 | > 0 |
| close | float64 | > 0 |
| volume | float64 | >= 0 |
-->

| フィールド | 型 | 制約 |
|---|---|---|
| {FIELD_1} | {TYPE_1} | {CONSTRAINT_1} |
| {FIELD_2} | {TYPE_2} | {CONSTRAINT_2} |

---

## 重要レイヤーの設計方針

<!-- 特に重要なレイヤーの処理フロー・制約を記載する。 -->
<!--
ex（Risk Management）:
signal = strategy.generate_signal()
order = risk_manager.validate(signal)   # ここでブロック or 通過
if order:
    execution.place_order(order)
-->

```
{PROCESSING_FLOW}
```

---

## 各フィーチャーの詳細設計

各フィーチャーの詳細設計は `.steering/{date}-{feature}/design.md` に記録される。
