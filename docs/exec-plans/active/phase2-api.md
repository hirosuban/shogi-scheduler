# Phase 2: Backend API

## 目標

Phase 1で構築したSQLiteのデータをフロントエンドに提供するREST APIを実装する。

## 背景・動機

フロントエンドはAPIを通じてデータを取得する。
Phase 1が完了し、SQLiteにデータが存在する状態で着手する。

## アプローチ

- `FastAPI` でAPIサーバーを構築
- `GET /tournaments` エンドポイントでエリア・日付・カテゴリの絞り込みをサポート
- APIはフロントエンドと別オリジンになるためCORSを設定する

## タスク

- [x] `src/api/` ディレクトリ作成・FastAPIプロジェクトセットアップ
- [x] SQLiteへの接続・クエリ実装
- [x] `GET /tournaments` エンドポイント実装
  - クエリパラメータ: `prefecture`（複数指定可）, `from`（日付）, `to`（日付）, `category`
  - レスポンス: JSON配列（id, date, name, venue, prefecture, category）
- [x] `GET /tournaments/{id}` エンドポイント実装（大会詳細）
- [x] CORSの設定（フロントエンドのオリジンを許可）
- [x] ローカルでの動作確認（各パラメータでの絞り込みが正常に動くこと）

## 意思決定ログ

- Phase 1の決定に合わせて `lat/lon`（`lat/lng`）はAPIレスポンス項目から除外した
- `category` はDB上の保存形式（カンマ区切り文字列）を維持し、APIも文字列として返す
- CORS許可オリジンは `FRONTEND_ORIGINS` 環境変数で上書き可能にし、ローカル開発用デフォルトを設定した

## 完了条件

- `GET /tournaments` が正常なJSONを返すこと
- エリア・日付・カテゴリの各フィルタが正しく動作すること
- フロントエンドのオリジンからのリクエストがCORSエラーなく通ること
