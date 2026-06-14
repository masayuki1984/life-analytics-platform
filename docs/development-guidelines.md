<!-- TEMPLATE: /setup-project を実行するか直接編集して、{PLACEHOLDER} を実際の値に書き換えてください。 -->
<!-- 記入後に <!-- ex: --> コメントと、このブロックを削除してください。 -->

# 開発規約

**最終更新**: {YYYY-MM-DD}
**ステータス**: 確定 | 草案 | 見直し中 | 廃止

---

## コーディング規約

- **型ヒント必須**（関数の引数・戻り値すべて）
- **docstring 必須**（{DOCSTRING_STYLE} スタイル） <!-- ex: NumPy スタイル / Google スタイル -->
- 1 クラス 1 責務の原則
- 設定値のハードコード禁止 — 設定ファイルか環境変数から取得
- 秘密鍵・API キーはコードに書かない。`.env` も git にコミットしない

### docstring スタイル

<!--
ex（NumPy スタイル）:
def fetch_data(source: str, limit: int) -> list[dict]:
    """
    データソースからレコードを取得する。

    Parameters
    ----------
    source : str
        データソース識別子（例: "api_v2"）
    limit : int
        取得件数上限

    Returns
    -------
    list[dict]
        取得したレコードのリスト

    Raises
    ------
    DataFetchError
        取得に失敗した場合
    """
-->

```{LANGUAGE}
{DOCSTRING_EXAMPLE}
```

### エラーハンドリング

- {ERROR_HANDLING_POLICY}
<!-- ex: 外部 API エラーは `{SRC_DIR}/utils/exceptions.py` の例外クラスを使う -->
<!-- ex: ログは `{SRC_DIR}/utils/logger.py` の logger を使用 -->

### Lint / Format

```bash
{LINT_COMMAND}   # ex: ruff check .
{FORMAT_COMMAND} # ex: ruff format . / prettier --write .
```

---

## ファイル・クラス命名規則

<!--
ex（Python）:
| 対象 | 規則 | 例 |
|---|---|---|
| ファイル | snake_case.py | ohlcv_handler.py |
| クラス | PascalCase | OhlcvHandler |
| 定数 | UPPER_SNAKE_CASE | MAX_RETRY_COUNT |
| テストファイル | test_{module_name}.py | test_ohlcv_handler.py |

ex（TypeScript）:
| 対象 | 規則 | 例 |
|---|---|---|
| ファイル | kebab-case.ts | user-profile.ts |
| クラス / 型 | PascalCase | UserProfile |
| 定数 | UPPER_SNAKE_CASE | MAX_RETRY_COUNT |
-->

| 対象 | 規則 | 例 |
|---|---|---|
| ソースファイル | {FILE_NAMING} | {FILE_EXAMPLE} |
| クラス | {CLASS_NAMING} | {CLASS_EXAMPLE} |
| 定数 | {CONST_NAMING} | {CONST_EXAMPLE} |
| テストファイル | {TEST_NAMING} | {TEST_EXAMPLE} |

---

## テスト規約

- `{TEST_DIR}/` 以下にテストを配置 <!-- ex: Test/ / tests/ / __tests__/ -->
- {MOCK_POLICY} <!-- ex: 外部 API のモックは pytest-mock を使用 -->
- 実際の外部 API を叩くテストは `{TEST_DIR}/integration/` 以下に分離し、CI では実行しない

---

## 依存管理

```bash
# インストール
{INSTALL_COMMAND}   # ex: uv sync --frozen / npm ci

# 依存追加
{ADD_COMMAND}       # ex: uv add {package} / npm install {package}

# スクリプト実行
{RUN_COMMAND}       # ex: uv run python main.py / npm run dev
```

### Docker でのセットアップ（該当する場合）

<!--
ex（uv）:
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen
COPY . .
-->

```dockerfile
{DOCKERFILE_SETUP}
```

---

## 外部サービス・インテグレーションの追加手順

<!-- 取引所・決済プロバイダー・外部 API などを追加するときの手順。不要なら削除する。 -->
<!--
ex（取引所）:
1. `Application/Formatter/{Exchange}/formatter.py` — HTTP API ラッパー
2. `Application/WS/{Exchange}/websocket.py` — WebSocket 接続
3. `Application/Const/authorized_key_list.py` — 対応シンボルを追記
-->

1. {STEP_1}
2. {STEP_2}
3. {STEP_3}

---

## ブランチ・コミット規約

### ブランチ名

```
{type}/{short-description}
```

例: `feature/user-auth`, `fix/login-redirect`

### コミットメッセージプレフィックス

| プレフィックス | 用途 |
|---|---|
| `[update]` | 機能追加・改善 |
| `[fix]` | バグ修正 |
| `[debug]` | デバッグ用の一時的な変更 |
| `[doc]` | ドキュメント更新 |
| `[refactor]` | リファクタリング |
| `[test]` | テスト追加・修正 |

---

## 開発フロー（スペック駆動）

1. `/add-feature {機能名}` を実行 — ステアリングドキュメントが `.steering/` に作成される
2. ステアリングドキュメントの設計を確認・承認してから実装開始
3. タスクリストの全項目を `[x]` にしてから完了とする
4. 実装前に CLAUDE.md → `docs/` → コードの grep の順で文脈を把握する
