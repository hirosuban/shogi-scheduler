# Phase 4: デプロイ準備・コード整理

## 目標

フロントエンドとバックエンドを一つのアプリケーションとして統合し、本番環境でシンプルに動作するように実装を整理する。

## 背景・動機

Phase 1〜3 が完了しローカルで動作している。
Phase 5 でのデプロイを円滑にするために、以下を整理・実装する：

- フロント + バックを同一 FastAPI アプリで配信（案 1）
- スクレイパーは GitHub Actions で定期実行（案 3）
- Render.com の無料枠でデプロイ可能な構成

## アプローチ

- `server.py` を作成し、FastAPI にフロントエンド静的ファイルをマウント
- CORS を同一オリジン用に調整（`CORSMiddleware` の設定を環境別に分岐）
- 環境変数を `ApiConfig` で管理し、開発・本番を切り替え可能に
- `render.json` または `Procfile` を追加（Render デプロイ時の自動検出用）
- スクレイパーのスケジューラー起動を削除（GitHub Actions で外部から呼び出す API エンドポイント準備）

## タスク

- [ ] `server.py` 作成（FastAPI + StaticFiles 統合）
- [ ] `src/api/main.py` の CORS 設定を環境別に分岐（開発: ワイルドカード、本番: localhost のみ）
- [ ] `src/api/config.py` を拡張（`ApiConfig` に `environment`、`frontend_origins` の動的設定）
- [ ] `render.json` 作成（Render の自動ビルド・起動設定）
- [ ] スクレイパー呼び出し用の内部 API エンドポイント追加（`POST /admin/trigger-scraper` など）
- [ ] ローカル動作確認（`server.py` or `uvicorn server:app` で フロント＋バック＋API が正常に動作することを確認）
- [ ] テスト追加（既存テスト + `server.py` の統合テスト）

## 意思決定ログ

- ホスティング先: **Render.com 無料枠**（完全無料、GitHub 連携が簡単）
- スクレイパー定期実行: **GitHub Actions**（外部スケジューラ、無料、管理が一箇所）
- フロント配信: FastAPI の `StaticFiles`（シンプル、CORS 削除可能）

## 完了条件

- `server.py` を起動するだけで、フロント + バック API の両方がローカルで動作する
- 環境変数 `ENVIRONMENT=production` で本番設定に自動切り替わる
- `render.json` が正しく配置され、Render Dashboard で自動検出される
- 内部 API エンドポイント（スクレイパートリガー）が完成している
