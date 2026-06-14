<!-- TEMPLATE: /setup-project を実行するか直接編集して、{PLACEHOLDER} を実際の値に書き換えてください。 -->
<!-- 記入後に <!-- ex: --> コメントと、このブロックを削除してください。 -->

# プロダクト要件定義（PRD）

**最終更新**: {YYYY-MM-DD}
**ステータス**: 確定 | 草案 | 見直し中 | 廃止

---

## 概要

{PROJECT_NAME} は {PROJECT_DESCRIPTION}。

**想定ユーザー**: {TARGET_USER}
<!-- ex: 開発者本人（個人運用） -->
<!-- ex: 社内の営業チーム（10〜50名） -->

---

## 対応サービス・インテグレーション

<!-- 外部サービス・データソース等を列挙する。不要なら削除する。 -->
<!--
ex（トレーディング）:
| 取引所 | 優先度 | 主要シンボル | 備考 |
|---|---|---|---|
| Bitbank | 高 | BTC_JPY, XRP_JPY | 現物のみ |
| BitFlyer | 高 | BTC_JPY | — |

ex（SaaS）:
| 外部サービス | 用途 | 備考 |
|---|---|---|
| Stripe | 決済処理 | Webhook 対応必須 |
| SendGrid | メール送信 | — |
-->

| {SERVICE} | {PRIORITY} | {DETAILS} | {NOTES} |
|---|---|---|---|
| | | | |

---

## 機能フェーズ

### フェーズ 1: {PHASE_1_NAME}（{STATUS}）
<!-- ex: フェーズ 1: 過去データ収集（最優先・未実装） -->

- {TASK_1}
- {TASK_2}

### フェーズ 2: {PHASE_2_NAME}（{STATUS}）
<!-- ex: フェーズ 2: バックテスト（未実装・旧実装あり） -->

- {TASK_1}
- {TASK_2}

### フェーズ 3: {PHASE_3_NAME}（{STATUS}）
<!-- ex: フェーズ 3: リスク管理（未実装・ライブトレード前に必須） -->

<!-- ⚠️ 重要な制約があれば明記する -->
<!-- ex: これがないと本番運用は行わない。 -->

- {TASK_1}
- {TASK_2}

---

## 主要インターフェース・操作一覧

<!-- モジュール・サービスが提供する主要な操作を列挙する。不要なら削除する。 -->
<!--
ex（PrivateAPI）:
共通:
- `order_market` / `order_limit`
- `get_position` / `cancel_all_orders`

ex（REST API）:
- `GET /api/v1/items`
- `POST /api/v1/items`
-->

{INTERFACE_CATEGORY}:
- `{operation_1}`
- `{operation_2}`

---

## バックログ（フェーズ完了後）

<!-- 将来的に取り組む項目。優先度・規模感も書いておくと後で判断しやすい。 -->

- {BACKLOG_ITEM_1}
- {BACKLOG_ITEM_2}
