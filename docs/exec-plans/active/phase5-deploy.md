# Phase 5: 本番デプロイ・定期実行設定

## 目標

Phase 4 の実装を Render.com に本番デプロイし、スクレイパーの定期実行を GitHub Actions で動作させる。

## 背景・動機

Phase 4 のコード整理が完了し、デプロイ準備が整った。
本番環境でアプリが継続的に動作し、スクレイパーデータが定期更新される状態を作る。

## アプローチ

- GitHub に `phase4-prepare-deployment` ブランチをマージ
- Render.com に GitHub リポジトリを連携し、ワンクリックデプロイ
- GitHub Actions ワークフロー作成（定期トリガー → Render API エンドポイント呼び出し）
- 本番環境での動作確認

## タスク

- [ ] GitHub に phase4 ブランチをプッシュ・PR マージ
- [ ] Render.com ダッシュボードで新しい Web Service を作成
- [ ] GitHub リポジトリ連携（自動デプロイ有効化）
- [ ] Render の環境変数設定（`ENVIRONMENT=production` など）
- [ ] `.github/workflows/scraper-schedule.yml` 作成（GitHub Actions）
  - 毎日 00:00 UTC に実行
  - Render API エンドポイント（`POST /admin/trigger-scraper`）を呼び出し
  - 成功・失敗をログに記録
- [ ] 本番 URL にアクセス → フロント画面が表示される確認
- [ ] 地図・フィルタ・API が正常に動作することを確認
- [ ] スクレイパーの定期実行が動作していることを確認（GitHub Actions ログ確認）
- [ ] 本番データが更新されていることを確認（DB を確認 or API レスポンス確認）

## 意思決定ログ

- スクレイパー定期実行: `uv run python show_db.py` の代わりに GitHub Actions で `curl -X POST` でエンドポイント呼び出し

## 完了条件

- 本番 URL（`https://myapp.render.com` など）でアプリが閲覧できる
- フロント画面・地図・API フィルタが正常に動作する
- GitHub Actions が定期的に実行され、スクレイパーが動作している
- 本番 DB のデータが定期的に更新されている
