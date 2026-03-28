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

- [ ] `src/api/` ディレクトリ作成・FastAPIプロジェクトセットアップ
- [ ] SQLiteへの接続・クエリ実装
- [ ] `GET /tournaments` エンドポイント実装
  - クエリパラメータ: `prefecture`（複数指定可）, `from`（日付）, `to`（日付）, `category`
  - レスポンス: JSON配列（id, date, name, venue, prefecture, category）
- [ ] `GET /tournaments/{id}` エンドポイント実装（大会詳細）
- [ ] CORSの設定（フロントエンドのオリジンを許可）
- [ ] ローカルでの動作確認（各パラメータでの絞り込みが正常に動くこと）

## 意思決定ログ

<!-- 途中で行った設計判断を記録 -->

## 完了条件

- `GET /tournaments` が正常なJSONを返すこと
- エリア・日付・カテゴリの各フィルタが正しく動作すること
- フロントエンドのオリジンからのリクエストがCORSエラーなく通ること
