<!-- TEMPLATE: /setup-project を実行するか直接編集して、{PLACEHOLDER} を実際の値に書き換えてください。 -->
<!-- 外部 I/F が存在しないプロジェクトはこのファイルごと削除してください。 -->
<!-- 記入後に <!-- ex: --> コメントと、このブロックを削除してください。 -->

# API 仕様

**最終更新**: {YYYY-MM-DD}
**ステータス**: 確定 | 草案 | 見直し中 | 廃止
**API 種別**: {API_TYPE}
<!-- ex: REST / GraphQL / WebSocket / 内部モジュール API / CLI -->

---

## 概要

<!--
ex（REST）:
- **ベース URL**: `https://api.example.com/v1`
- **認証方式**: Bearer トークン（JWT）
- **データ形式**: JSON（`Content-Type: application/json`）

ex（内部モジュール API）:
- **インターフェース**: Python 抽象クラス `PublicAPI` / `PrivateAPI`
- **実装場所**: `{SRC_DIR}/API/`
- **呼び出し元**: `{SRC_DIR}/Client/`
-->

- **{KEY_1}**: {VALUE_1}
- **{KEY_2}**: {VALUE_2}
- **{KEY_3}**: {VALUE_3}

---

## 認証

<!--
ex（API キー）:
すべてのリクエストに `Authorization: Bearer {token}` ヘッダーを付与する。
API キーは `.env` の `API_KEY` から取得する。コードにハードコードしない。

ex（HMAC 署名）:
リクエストごとに HMAC-SHA256 でシグネチャを生成し、ヘッダーに付与する。
取引所 API によく使われる方式。

ex（認証なし / 内部 API）:
内部モジュール間通信のため認証不要。
-->

{AUTH_DESCRIPTION}

---

## 共通規約

### リクエスト / レスポンス形式

<!--
ex（REST JSON）:
- リクエスト: `Content-Type: application/json`
- レスポンス: JSON。成功時は `200 OK` + ペイロード、エラー時は `4xx` / `5xx` + エラーオブジェクト

ex（内部 API）:
- 引数: Python 型ヒント付き。Pydantic モデルで入力バリデーションを行う
- 戻り値: TypedDict または dataclass。`None` は返さず例外を使う
-->

{REQUEST_RESPONSE_CONVENTION}

### エラー形式

<!--
ex（REST）:
```json
{
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "symbol は BTC_JPY 形式で指定してください",
    "detail": {}
  }
}
```

ex（内部 API / 例外）:
```python
raise ExchangeAPIError(code="RATE_LIMIT", message="レートリミット超過", retry_after=1.0)
```
-->

```
{ERROR_FORMAT_EXAMPLE}
```

### ページネーション（該当する場合）

<!--
ex（カーソルベース）:
- リクエスト: `?limit=100&cursor={cursor}`
- レスポンス: `{ "data": [...], "next_cursor": "xxx", "has_more": true }`

ex（オフセットベース）:
- リクエスト: `?limit=100&offset=0`
- レスポンス: `{ "data": [...], "total": 500 }`
-->

{PAGINATION_DESCRIPTION}

---

## エンドポイント / メソッド一覧

<!--
ex（REST）:
| メソッド | パス | 説明 |
|---|---|---|
| GET | `/ohlcv` | OHLCV データ取得 |
| POST | `/orders` | 注文作成 |
| DELETE | `/orders/{id}` | 注文キャンセル |

ex（内部 API）:
| メソッド名 | クラス | 説明 |
|---|---|---|
| `get_ohlcv()` | `PublicAPI` | OHLCV データ取得 |
| `order_market()` | `PrivateAPI` | 成行注文 |
| `cancel_all_orders()` | `PrivateAPI` | 全注文キャンセル |
-->

| {COL_1} | {COL_2} | 説明 |
|---|---|---|
| {ITEM_1} | {DETAIL_1} | {DESCRIPTION_1} |
| {ITEM_2} | {DETAIL_2} | {DESCRIPTION_2} |

---

## エンドポイント詳細

<!--
セクションを繰り返してエンドポイントごとに記述する。
不要なフィールド（Query Params が存在しない等）は削除してよい。
-->

### {ENDPOINT_1_NAME}

<!--
ex: ### GET /ohlcv — OHLCV データ取得
ex: ### `order_market(symbol, size, side)` — 成行注文
-->

**{METHOD}** `{PATH_OR_SIGNATURE}`

{BRIEF_DESCRIPTION}

#### パラメータ

<!--
ex（REST クエリパラメータ）:
| パラメータ | 型 | 必須 | 説明 |
|---|---|---|---|
| `exchange` | string | ✓ | 取引所名（例: `bitbank`） |
| `symbol` | string | ✓ | シンボル（例: `BTC_JPY`） |
| `limit` | integer | — | 取得件数（デフォルト: 100、最大: 1000） |

ex（関数引数）:
| 引数 | 型 | デフォルト | 説明 |
|---|---|---|---|
| `symbol` | `str` | — | シンボル（例: `BTC_JPY`） |
| `size` | `float` | — | 注文サイズ（BTC 単位） |
| `side` | `Literal["buy", "sell"]` | — | 売買方向 |
-->

| パラメータ / 引数 | 型 | 必須 | 説明 |
|---|---|---|---|
| `{PARAM_1}` | {TYPE_1} | {REQUIRED_1} | {DESC_1} |
| `{PARAM_2}` | {TYPE_2} | {REQUIRED_2} | {DESC_2} |

#### レスポンス / 戻り値

<!--
ex（REST JSON レスポンス）:
```json
{
  "data": [
    { "timestamp": 1714000000000, "open": 9500000, "high": 9600000, "low": 9400000, "close": 9550000, "volume": 1.5 }
  ]
}
```

ex（Python 戻り値）:
```python
Order(id="abc123", symbol="BTC_JPY", size=0.01, side="buy", status="open")
```
-->

```
{RESPONSE_EXAMPLE}
```

#### エラー / 例外

<!--
ex:
| コード / 例外 | 説明 |
|---|---|
| `400 INVALID_SYMBOL` | 未対応のシンボルが指定された |
| `429 RATE_LIMIT` | レートリミット超過。1 秒後にリトライ |
| `ExchangeAPIError` | 取引所 API からエラーが返った場合 |
-->

| コード / 例外 | 説明 |
|---|---|
| {ERROR_CODE_1} | {ERROR_DESC_1} |
| {ERROR_CODE_2} | {ERROR_DESC_2} |

---

## レート制限（該当する場合）

<!--
ex:
| 取引所 | 上限 | 超過時の挙動 |
|---|---|---|
| Bitbank | 約 10 req/sec | HTTP 429 → 1 秒待機してリトライ |
| BitFlyer | 約 2 req/sec | HTTP 429 → 0.5 秒待機してリトライ |
-->

| {SERVICE} | {LIMIT} | {BEHAVIOR} |
|---|---|---|
| {VALUE_1} | {VALUE_2} | {VALUE_3} |

---

## 変更履歴

| 日付 | バージョン | 変更内容 |
|---|---|---|
| {YYYY-MM-DD} | {VERSION} | 初版作成 |
