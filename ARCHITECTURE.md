# ARCHITECTURE.md

このドキュメントはコードベースのトップレベルマップです。
ドメイン構造・パッケージ階層・依存関係ルールを定義します。

> **注意**: このドキュメントは実際のコード構造と常に同期させること。
> 乖離を発見した場合は同じPRで更新してください。

---

## ディレクトリ構造

```
/
├── .devcontainer/         # 開発環境定義
├── AGENTS.md              # エージェントへのマップ
├── ARCHITECTURE.md        # このファイル
├── docs/                  # ナレッジベース（記録システム）
└── src/
    ├── scraper/           # Blogspotスクレイピング・ジオコーディング
    ├── api/               # FastAPI（REST API・スケジューラ）
    └── frontend/          # 生HTML + Vanilla JS + Leaflet.js
```

---

## レイヤードアーキテクチャ

各ビジネスドメインは以下の固定レイヤー群に分割されます。
依存関係は **前方方向のみ** 許可されます（後戻り禁止）。

```
types → config → repository → service → api/runtime → ui
```

| レイヤー | 役割 |
|---|---|
| `types` | データ形状の定義。外部依存なし |
| `config` | 設定値の読み込み・バリデーション |
| `repository` | データアクセス（DB・外部API） |
| `service` | ビジネスロジック |
| `api/runtime` | エントリポイント・ルーティング |
| `ui` | プレゼンテーション層 |

---

## 横断的関心事（Cross-cutting Concerns）

以下は単一の明示的なインターフェース（**Provider**）を通じてのみ処理します。
各レイヤーへの直接依存は禁止します。

- 認証・認可
- テレメトリ（ログ・メトリクス・トレース）
- 機能フラグ

---

## 依存関係ルール

- **前方依存のみ**: 上位レイヤーから下位レイヤーへの参照のみ許可
- **横断的関心事**: Provider 経由のみ
- **ドメイン間**: 明示的に定義された公開インターフェース経由のみ
- **境界でのバリデーション**: 外部入力はすべて境界でスキーマ検証を行う

これらのルールはカスタムリンターと構造テストで機械的に適用します。

---

## ビジネスドメイン

- `tournaments` — 大会情報の管理・APIへの公開
- `scraper` — 外部サイトからのデータ収集・ジオコーディング

---

## 技術スタック

| 領域 | 技術 |
|---|---|
| 開発環境 | devcontainer |
| 依存管理 | uv |
| フロントエンド | 生HTML + Vanilla JS + Leaflet.js |
| バックエンド | Python / FastAPI |
| スクレイピング | requests + BeautifulSoup4 |
| ジオコーディング | Nominatim (OpenStreetMap) |
| データベース | SQLite |
| スケジューラ | APScheduler |
| ホスティング（フロント） | Vercel ※暫定 |
| ホスティング（バックエンド） | Render または Fly.io ※暫定 |

> 技術選定の理由は [`docs/design-docs/tech-stack.md`](./docs/design-docs/tech-stack.md) を参照。
