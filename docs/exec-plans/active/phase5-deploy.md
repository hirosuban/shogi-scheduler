# Phase 5: 本番デプロイ・定期実行設定

## 目標

Phase 4 の実装を Render.com に本番デプロイし、スクレイパーの定期実行を GitHub Actions で動作させる。

## 背景・動機

Phase 4 のコード整理が完了し、デプロイ準備が整った。
本番環境でアプリが継続的に動作し、スクレイパーデータが定期更新される状態を作る。

## アプローチ

- GitHub に main ブランチを最新化
- Render.com に GitHub リポジトリを連携し、ワンクリックデプロイ
- GitHub Actions ワークフロー作成（定期トリガー → Render Deploy Hook 呼び出し、またはスクレイパーエンドポイント呼び出し）
- 本番環境での動作確認

---

## フェーズ別タスク

### Phase A: 人間が事前に準備すること（エージェント起動前に完了）

エージェントはこれらのリソースや認証情報に直接アクセスできないため、人間が手動で実施する。

- [ ] **Render アカウント作成**
  - https://render.com でサインアップ（GitHub アカウント連携推奨）

- [ ] **Render で Web Service を作成**
  - ダッシュボード → "New Web Service" → GitHub リポジトリを選択
  - `render.json` の内容が自動反映されることを確認
    - Build: `uv sync && uv run pip install -e .`
    - Start: `uv run uvicorn server:app --host 0.0.0.0 --port ${PORT:-8000}`
  - Environment: `ENVIRONMENT=production` が設定されていることを確認
  - デプロイが完了し、本番 URL（`https://xxxx.onrender.com`）が発行されることを確認

- [ ] **Render の Deploy Hook URL を取得**
  - Render ダッシュボード → 対象サービス → "Settings" → "Deploy Hook" をコピー
  - 形式: `https://api.render.com/deploy/srv-xxx?key=yyy`

- [ ] **GitHub Secrets に登録**
  - リポジトリの Settings → Secrets and variables → Actions → "New repository secret"
  - `RENDER_DEPLOY_HOOK_URL`: 上記でコピーした Deploy Hook URL
  - `RENDER_APP_URL`: 本番 URL（例: `https://xxxx.onrender.com`）
    - GitHub Actions からスクレイパーエンドポイントを叩くために使用

- [ ] **エージェントに以下を共有する**（作業開始時に伝える）
  - 本番 URL（`https://xxxx.onrender.com`）

### Phase B: エージェントが実行すること（Phase A 完了後）

上記の Secrets と本番 URL が準備できたらエージェントに依頼する。

- [ ] `.github/workflows/scraper-schedule.yml` 作成
  - cron: 毎日 JST 9:00（= UTC 00:00）に実行
  - `POST $RENDER_APP_URL/admin/trigger-scraper` を呼び出し
  - HTTP ステータスが 2xx でなければ workflow を失敗させる
  - 成功・失敗をログに記録

- [ ] 本番 URL での動作確認（スモークテスト）
  - フロント画面が表示されるか `curl` で確認
  - `/api/tournaments` が JSON を返すか確認
  - `/admin/trigger-scraper` が 200 を返すか確認

- [ ] GitHub Actions の初回手動実行 → ログで成功確認

### Phase C: 人間が最終確認すること

- [ ] ブラウザで本番 URL を開き、地図・フィルタが正常に動作することを目視確認
- [ ] 翌日以降、GitHub Actions の定期実行ログを確認
- [ ] 本番 DB のデータが更新されていることを確認

---

## 意思決定ログ

- スクレイパー定期実行: Render の Cron Job 機能ではなく GitHub Actions から `POST /admin/trigger-scraper` を呼び出す方式を採用（無料枠の制約回避・ログ可視性のため）
- Deploy Hook を使う理由: Render API Key よりスコープが限定的でセキュリティリスクが低い

## 完了条件

- 本番 URL（`https://xxxx.onrender.com`）でアプリが閲覧できる
- フロント画面・地図・API フィルタが正常に動作する
- GitHub Actions が定期的に実行され、スクレイパーが動作している
- 本番 DB のデータが定期的に更新されている
