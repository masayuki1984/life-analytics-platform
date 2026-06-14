<!--
==============================================================
TEMPLATE USAGE（記入後にこのブロックごと削除する）
==============================================================
このファイルは Claude Code スペック駆動開発用の CLAUDE.md テンプレートです。

【記入方法】
1. `/setup-project` を実行すると Claude Code が対話形式でプレースホルダーを埋めます。
2. 手動で記入する場合は `{PLACEHOLDER}` をすべて実際の値に置き換えてください。
3. 各プレースホルダーの直後にある `<!-- ex: ... -->` が記入例です。
   記入完了後、<!-- ex: ... --> コメントはすべて削除してください。
4. 「※ 不要なら削除する」と書かれたセクションはプロジェクトに不要なら削除してください。

【Claude Code への指示】
- このブロック（TEMPLATE USAGE）は記入完了後に削除する。
- <!-- ex: --> コメントは値を記入したら削除する。
- セクション末尾の「※ 不要なら削除する」注記も削除する。
==============================================================
-->

# {PROJECT_NAME} - Claude Code 開発ガイド <!-- ex: AlgoQ Framework -->

## プロジェクト概要

{PROJECT_NAME} は {LANGUAGE} ベースの {PROJECT_DESCRIPTION}。
<!-- ex: AlgoQ Framework は Python ベースの暗号通貨アルゴリズムトレーディングフレームワーク。 -->

**主要機能**:
1. **{FEATURE_1}** — {FEATURE_1_DESCRIPTION}
2. **{FEATURE_2}** — {FEATURE_2_DESCRIPTION}
3. **{FEATURE_3}** — {FEATURE_3_DESCRIPTION}
<!--
ex:
1. **過去データ収集** — OHLCV・約定履歴等を取得し S3 へ永続化
2. **バックテスト** — 収集した過去データを用いた戦略検証
3. **ライブトレード** — 実際の取引所への注文・ポジション管理
-->

---

## 技術スタック

### 現行（既存コードベース）
- **言語**: {LANGUAGE} {VERSION} <!-- ex: Python 3.12 -->
- **依存管理**: {PACKAGE_MANAGER}（`{MANIFEST_FILE}` + `{LOCKFILE}`） <!-- ex: uv（`pyproject.toml` + `uv.lock`） -->
- **テスト**: {TEST_FRAMEWORK}（`{TEST_DIR}` ディレクトリ） <!-- ex: pytest（`Test/` ディレクトリ） -->
- **コンテナ**: {CONTAINER_TOOL} <!-- ex: Docker / docker-compose -->
- **ストレージ**: {STORAGE_TOOL} <!-- ex: AWS S3（boto3）または Cloudflare R2 -->
- **主要ライブラリ**: {MAIN_LIBRARIES} <!-- ex: pandas, numpy, ccxt, boto3, requests, pyyaml -->

### 新規モジュールで採用を検討するモダンスタック

<!--
ex:
| カテゴリ | 推奨 | 理由 |
|---|---|---|
| 依存管理 | **uv** | pip/Poetry より 10-100x 速い。仮想環境・ロックファイル・Python バージョン管理を一括 |
| データ処理 | **Polars** | pandas より高速。時系列の groupby・rolling に強い |
| Lint/Format | **Ruff** | flake8 + black + isort を 1 ツールで代替 |
-->

| カテゴリ | 推奨 | 理由 |
|---|---|---|
| {CATEGORY_1} | **{TOOL_1}** | {REASON_1} |
| {CATEGORY_2} | **{TOOL_2}** | {REASON_2} |
| {CATEGORY_3} | **{TOOL_3}** | {REASON_3} |

> 既存コードの書き換えは不要。**新規モジュールから段階的に採用**する。

---

## ディレクトリ構造

<!--
ex:
algo-q-framework/
├── CLAUDE.md
├── .claude/
│   ├── settings.json
│   ├── commands/
│   └── skills/
├── docs/
├── .steering/
├── Application/
│   ├── API/
│   ├── BackTest/
│   └── Crawler/
├── Test/
└── Deploy/
-->

```
{PROJECT_ROOT}/                           <!-- ex: algo-q-framework/ -->
├── CLAUDE.md                             # このファイル
├── .claude/
│   ├── settings.json                     # スキル権限設定
│   ├── commands/                         # カスタムスラッシュコマンド
│   └── skills/                           # カスタムスキル
├── docs/                                 # 永続ドキュメント（PRD・設計・規約等）
├── .steering/                            # セッション別作業ドキュメント
├── {SRC_DIR}/                            <!-- ex: Application/ -->
│   ├── {MODULE_1}/                       # {MODULE_1_DESCRIPTION} <!-- ex: API/ — PublicAPI / PrivateAPI インターフェース -->
│   ├── {MODULE_2}/                       # {MODULE_2_DESCRIPTION} <!-- ex: BackTest/ — バックテスト -->
│   └── {MODULE_3}/                       # {MODULE_3_DESCRIPTION} <!-- ex: Crawler/ — データ収集 -->
├── {TEST_DIR}/                           # テスト <!-- ex: Test/ -->
└── {DOCS_DIR}/                           # ドキュメント <!-- ex: Document/ -->
```

### 主要モジュールの役割

<!--
ex:
| モジュール | 役割 |
|---|---|
| `Application/Formatter/{Exchange}/formatter.py` | 取引所 API の薄いラッパー（HTTP リクエスト送信） |
| `Application/WS/{Exchange}/websocket.py` | WebSocket 接続・購読管理 |
| `Application/AppUtility/aws/s3_handle.py` | S3 アクセス |
-->

| モジュール | 役割 |
|---|---|
| `{MODULE_PATH_1}` | {MODULE_ROLE_1} |
| `{MODULE_PATH_2}` | {MODULE_ROLE_2} |
| `{MODULE_PATH_3}` | {MODULE_ROLE_3} |

---

## 開発プロセス（スペック駆動開発）

### 基本原則

1. **永続ドキュメント**（`docs/`）に「何を作るか」を定義する
2. **ステアリングドキュメント**（`.steering/`）で「今日何をするか」を管理する
3. タスクリストの全項目を `[x]` にしてから完了とする
4. 実装前に CLAUDE.md → 永続ドキュメント → コードの grep の順で文脈を把握する

### ワークフロー

- 初回セットアップ: `/setup-project` → 永続ドキュメントをインタラクティブに作成
- フィーチャー追加: `/add-feature [機能名]` → 要件定義→設計→実装→テストを自動進行
- 通常の修正・質問: 通常の会話で対応

### ドキュメント構成

```
docs/
├── product-requirements.md    # プロダクト要件定義書（何を・なぜ作るか）
├── architecture.md            # システム設計・モジュール構成
├── development-guidelines.md  # コーディング規約・レビュー基準
├── api-spec.md                # API 仕様（外部 I/F がある場合）
└── data-spec.md               # データスキーマ・フォーマット仕様

.steering/
└── {YYYYMMDD}-{task-name}.md  # セッション単位の作業ドキュメント
```

**ステアリングドキュメントのフォーマット**:
```markdown
# {タスク名}

## 目的
{このセッションで達成すること}

## タスクリスト
- [ ] {タスク 1}
- [ ] {タスク 2}
- [ ] {タスク 3}

## 完了条件
{何をもって完了とするか}
```

---

## コーディング規約

### {LANGUAGE} <!-- ex: Python -->

- **型ヒント必須**（関数の引数・戻り値）
- **docstring 必須**（{DOCSTRING_STYLE} スタイル — `docs/development-guidelines.md` 参照） <!-- ex: NumPy スタイル -->
- 1 クラス 1 責務の原則
- エラーハンドリング: {ERROR_HANDLING_POLICY} <!-- ex: 取引所 API エラーは `AppUtility/exceptions.py` の例外を使う -->
- ログ: {LOGGING_POLICY} <!-- ex: `AppUtility/log.py` の logger を使用 -->
- 設定値: ハードコード禁止。設定ファイルか環境変数から取得
- 秘密鍵・API キー: コードに書かない。`.env` も git にコミットしない

### テスト

- `{TEST_DIR}/` 以下にテストを配置 <!-- ex: Test/ -->
- テストの粒度: 単体テスト + 統合テスト
- ファイル名: `test_{module_name}.{EXT}` <!-- ex: test_ohlcv_handler.py -->

### Lint / Format

```bash
{LINT_COMMAND}    # ex: ruff check .
{FORMAT_COMMAND}  # ex: ruff format .
```

### 依存管理

```bash
# インストール
{INSTALL_COMMAND}         # ex: uv sync --frozen

# 追加
{ADD_DEPENDENCY_COMMAND}  # ex: uv add pandas
```

### ファイル命名

- ソースファイル: `{FILE_NAMING_CONVENTION}` <!-- ex: snake_case.py -->
- クラス: `{CLASS_NAMING_CONVENTION}` <!-- ex: PascalCase -->
- 定数: `{CONST_NAMING_CONVENTION}` <!-- ex: UPPER_SNAKE_CASE -->

---

## データフォーマット仕様

> ※ このセクションはデータスキーマが重要なプロジェクト向け。不要なら削除する。

### {MAIN_DATA_SCHEMA} スキーマ <!-- ex: OHLCV スキーマ -->

<!--
ex:
| カラム | 型 | 制約 |
|---|---|---|
| timestamp | int64 | UTC Unix ミリ秒、単調増加 |
| open | float64 | > 0 |
| high | float64 | >= max(open, close) |
| close | float64 | > 0 |
| volume | float64 | >= 0 |
-->

| カラム / フィールド | 型 | 制約 |
|---|---|---|
| {FIELD_1} | {TYPE_1} | {CONSTRAINT_1} |
| {FIELD_2} | {TYPE_2} | {CONSTRAINT_2} |
| {FIELD_3} | {TYPE_3} | {CONSTRAINT_3} |

---

## 外部サービス・API

> ※ このセクションは外部 API を利用するプロジェクト向け。不要なら削除する。

### {SERVICE_NAME} <!-- ex: Bitbank -->

<!--
ex:
| エラー | 対処 |
|---|---|
| HTTP 429 | レートリミット。1 秒待機してリトライ |
| HTTP 401 | APIキー無効。`.env` を確認 |
-->

| エラー | 対処 |
|---|---|
| {ERROR_1} | {ACTION_1} |
| {ERROR_2} | {ACTION_2} |

---

## 重要な制約・注意事項

<!--
ex:
- `Application/Const/authorized_key_list.py` に対応取引所・シンボルの一覧がある。新規追加時はここも更新する
- Bitbank は現物のみ（無期限契約なし）
- WebSocket が切れた場合の再接続ロジックは `WS/ws_handler.py` が管理する
-->

- {CONSTRAINT_1}
- {CONSTRAINT_2}
- {CONSTRAINT_3}

---

## 実装状況

### 実装済み

<!--
ex:
- 取引所 WS 接続（Bitbank・BitFlyer・Bitmex）
- PrivateAPI / PublicAPI 統一インターフェース
- テクニカル指標（SMA・EMA・RSI・MACD・ATR）
-->

- {DONE_1}
- {DONE_2}
- {DONE_3}

### 未実装（実装順）

<!--
ex:
**フェーズ 1: 過去データ収集**
- `Application/DataCollection/` — REST API で OHLCV を取得し S3 へ Parquet 形式で永続化
- 差分取得・スケジュール実行対応
-->

**フェーズ 1: {PHASE_1_NAME}** <!-- ex: 過去データ収集 -->
- {PHASE_1_TASK_1}
- {PHASE_1_TASK_2}

**フェーズ 2: {PHASE_2_NAME}** <!-- ex: バックテストエンジン -->
- {PHASE_2_TASK_1}
- {PHASE_2_TASK_2}

**フェーズ 3: {PHASE_3_NAME}** <!-- ex: リスク管理 -->
- {PHASE_3_TASK_1}
- {PHASE_3_TASK_2}
