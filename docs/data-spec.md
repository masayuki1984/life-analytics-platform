<!-- TEMPLATE: /setup-project を実行するか直接編集して、{PLACEHOLDER} を実際の値に書き換えてください。 -->
<!-- データスキーマが単純なプロジェクトは architecture.md に統合し、このファイルごと削除してください。 -->
<!-- 記入後に <!-- ex: --> コメントと、このブロックを削除してください。 -->

# データ仕様

**最終更新**: {YYYY-MM-DD}
**ステータス**: 確定 | 草案 | 見直し中 | 廃止

---

## 概要

<!--
ex（トレーディング）: 取引所から収集した OHLCV・約定履歴を S3 に Parquet 形式で保存する。
ex（Web アプリ）: ユーザー・注文・商品データを PostgreSQL に保存する。
ex（データパイプライン）: 外部 API から取得した JSON を正規化して BigQuery に保存する。
-->

{DATA_OVERVIEW}

---

## データモデル一覧

<!--
ex（トレーディング）:
| モデル名 | 説明 | 保存先 |
|---|---|---|
| OHLCV | 時系列の価格データ | S3（Parquet） |
| Trade | 約定履歴 | S3（Parquet） |
| Order | 注文記録 | S3（JSON） |

ex（Web アプリ）:
| モデル名 | 説明 | 保存先 |
|---|---|---|
| User | ユーザー情報 | PostgreSQL `users` |
| Order | 注文情報 | PostgreSQL `orders` |
| Product | 商品マスタ | PostgreSQL `products` |
-->

| モデル名 | 説明 | 保存先 |
|---|---|---|
| {MODEL_1} | {DESC_1} | {STORAGE_1} |
| {MODEL_2} | {DESC_2} | {STORAGE_2} |

---

## データモデル詳細

<!--
セクションを繰り返してモデルごとに記述する。
-->

### {MODEL_1_NAME}

<!--
ex: ### OHLCV — 時系列価格データ
ex: ### User — ユーザー情報
-->

{MODEL_DESCRIPTION}

#### スキーマ

<!--
ex（Parquet / DataFrame）:
| カラム | 型 | 制約 |
|---|---|---|
| timestamp | int64 | UTC Unix ミリ秒、単調増加、NOT NULL |
| open | float64 | > 0、NOT NULL |
| high | float64 | >= max(open, close)、NOT NULL |
| low | float64 | <= min(open, close)、NOT NULL |
| close | float64 | > 0、NOT NULL |
| volume | float64 | >= 0、NOT NULL |

ex（DB テーブル）:
| カラム | 型 | 制約 |
|---|---|---|
| id | UUID | PRIMARY KEY |
| email | VARCHAR(255) | UNIQUE、NOT NULL |
| created_at | TIMESTAMPTZ | NOT NULL、DEFAULT now() |
-->

| フィールド / カラム | 型 | 制約 |
|---|---|---|
| {FIELD_1} | {TYPE_1} | {CONSTRAINT_1} |
| {FIELD_2} | {TYPE_2} | {CONSTRAINT_2} |
| {FIELD_3} | {TYPE_3} | {CONSTRAINT_3} |

#### バリデーションルール

<!--
ex（OHLCV）:
- NaN 禁止（バックテストデータとして使用するため）
- high >= max(open, close) かつ low <= min(open, close) を満たすこと
- timestamp は UTC で保存し、ローカル時刻に変換しない

ex（User）:
- email はメールアドレス形式であること
- password は平文で保存しない（bcrypt ハッシュ化）
-->

- {RULE_1}
- {RULE_2}

#### サンプルデータ

<!--
ex（JSON）:
```json
{ "timestamp": 1714000000000, "open": 9500000.0, "high": 9600000.0, "low": 9400000.0, "close": 9550000.0, "volume": 1.5 }
```

ex（SQL INSERT）:
```sql
INSERT INTO users (id, email, created_at) VALUES ('uuid-xxx', 'user@example.com', NOW());
```
-->

```
{SAMPLE_DATA}
```

---

## ストレージ・永続化設計

### 保存先と形式

<!--
ex（S3 + Parquet）:
| データ | 形式 | 保存先 |
|---|---|---|
| OHLCV | Parquet | S3 |
| 注文記録 | JSON | S3 |

ex（RDBMS）:
| データ | 形式 | 保存先 |
|---|---|---|
| ユーザー情報 | — | PostgreSQL |
| セッション | — | Redis |
-->

| データ | 形式 | 保存先 |
|---|---|---|
| {DATA_1} | {FORMAT_1} | {DEST_1} |
| {DATA_2} | {FORMAT_2} | {DEST_2} |

### パス規約 / 命名規則

<!--
ex（S3）:
```
s3://{bucket}/{exchange}/{symbol}/{timeframe}/{YYYY}/{MM}/{DD}.parquet
```
例: `s3://my-data/bitbank/BTC_JPY/1h/2026/06/06.parquet`
- exchange: 小文字（`bitbank`, `bitflyer`）
- symbol: 取引所表記に合わせる（`BTC_JPY`）
- timeframe: ccxt 表記（`1m`, `5m`, `1h`, `1d`）

ex（ローカルファイル）:
```
./data/{category}/{YYYY-MM-DD}.{ext}
```

ex（DB テーブル命名）:
- テーブル名: 複数形 + スネークケース（`users`, `order_items`）
- インデックス名: `idx_{table}_{column}`
-->

```
{PATH_PATTERN}
```

### パーティション / インデックス設計（該当する場合）

<!--
ex（Parquet パーティション）:
日付（YYYY/MM/DD）でパーティションを切ることで、日付範囲クエリの I/O を最小化する。

ex（DB インデックス）:
- `users(email)` — ログイン時の検索
- `orders(user_id, created_at)` — ユーザーごとの注文履歴
-->

{PARTITION_OR_INDEX_DESIGN}

---

## データライフサイクル

<!--
ex（S3 保管ポリシー）:
- 生データ（Raw）: 無期限保存
- 加工済みデータ: 最新 1 年分のみ保持
- バックアップ: S3 バージョニングを有効化

ex（DB）:
- ログテーブルは 90 日でアーカイブ
- 削除は物理削除ではなく `deleted_at` による論理削除
-->

- {LIFECYCLE_RULE_1}
- {LIFECYCLE_RULE_2}

---

## 変更履歴

| 日付 | 変更内容 |
|---|---|
| {YYYY-MM-DD} | 初版作成 |
