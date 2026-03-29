# Phase 5: 本番デプロイ・定期実行設定

## 目標

Phase 4 の実装を Render.com に本番デプロイし、スクレイパーの定期実行を GitHub Actions で動作させる。
SQLite は Render 上で永続化せず、GitHub Actions で更新した `data/shogi.db` をリポジトリにコミットして配信する。

## 背景・動機

Phase 4 のコード整理が完了し、デプロイ準備が整った。
本番環境でアプリが継続的に動作し、スクレイパーデータが定期更新される状態を作る。

## アプローチ

- GitHub に main ブランチを最新化
- Render.com に GitHub リポジトリを連携し、ワンクリックデプロイ
- GitHub Actions ワークフロー作成（定期トリガー → scraper 実行 → `data/shogi.db` をコミット）
- 本番環境での動作確認

---

## フェーズ別タスク

### Phase A: 人間が事前に準備すること（エージェント起動前に完了）

エージェントはこれらのリソースや認証情報に直接アクセスできないため、人間が手動で実施する。

- [x] **Render アカウント作成**
  - https://render.com でサインアップ（GitHub アカウント連携推奨）

- [x] **Render で Web Service を作成**
  - ダッシュボード → "New Web Service" → GitHub リポジトリを選択
  - `render.json` の内容が自動反映されることを確認
    - Build: `uv sync && uv run pip install -e .`
    - Start: `uv run uvicorn server:app --host 0.0.0.0 --port ${PORT:-8000}`
  - Environment: `ENVIRONMENT=production` が設定されていることを確認
  - デプロイが完了し、本番 URL（`https://xxxx.onrender.com`）が発行されることを確認

- [x] **Render の Auto Deploy を確認**
  - GitHub 連携済みサービスで Auto Deploy を ON にする
  - main ブランチ更新時に自動デプロイされることを確認

- [x] **GitHub Secrets に登録**
  - リポジトリの Settings → Secrets and variables → Actions → "New repository secret"
  - （この方式では必須 secret なし）
  - 任意: `RENDER_DEPLOY_HOOK_URL`（Auto Deploy を使わない場合のみ）
  - 不要なのでやっていません。（ユーザメモ）

- [x] **エージェントに以下を共有する**（作業開始時に伝える）
  - 本番 URL（`https://xxxx.onrender.com`）

### Phase B: エージェントが実行すること（Phase A 完了後）

上記の Secrets と本番 URL が準備できたらエージェントに依頼する。

- [x] `.github/workflows/scraper-schedule.yml` 作成
  - cron: 毎日 JST 9:00（= UTC 00:00）に実行
  - GitHub Actions 上で `uv run python -m src.scraper` を実行
  - `data/shogi.db` が更新されたら main ブランチへ自動コミット
  - コミットをトリガーに Render 側で自動デプロイ

- [x] 本番 URL での動作確認（スモークテスト）
  - フロント画面が表示されるか `curl` で確認
  - `/tournaments` が JSON を返すか確認
  - GitHub Actions 実行後のデプロイで `/tournaments` が 500 にならないことを確認

- [x] GitHub Actions の初回手動実行 → ログで成功確認

### Phase C: 人間が最終確認すること

- [x] ブラウザで本番 URL を開き、地図・フィルタが正常に動作することを目視確認
- [x] 翌日以降、GitHub Actions の定期実行ログを確認
- [x] 本番 DB（配信中 `data/shogi.db`）のデータが更新されていることを確認

---

## 意思決定ログ

- スクレイパー定期実行: Render の Cron Job/Persistent Disk は使わず、GitHub Actions で scraper 実行 + `data/shogi.db` コミット方式を採用（無料運用のため）
- デプロイ方式: Render は GitHub 連携の Auto Deploy を利用（Deploy Hook は任意）
- DB 構成: Render インスタンスでは DB を更新せず、ビルド成果物として `data/shogi.db` を同梱して配信する

## 実施ログ（2026-03-29）

- [x] `.github/workflows/scraper-schedule.yml` を作成
- [x] 本番 URL を共有済み: `https://shogi-scheduler.onrender.com/`
- [x] 有料 Persistent Disk を使わない方針に変更
- [x] スモークテスト結果
  - `GET /` → `200`
  - `GET /api/tournaments` → `404`（実際の API パスは `/tournaments`）
  - `GET /tournaments` → `500`
  - `POST /admin/trigger-scraper`（token なし）→ `403`

## DB チェックリスト（無料運用）

- [x] GitHub Actions が `data/shogi.db` を更新してコミットできる
- [x] Render Auto Deploy により最新コミットが本番へ反映される
- [x] 反映後に `/tournaments` が 500 にならず JSON を返す

## クローズメモ

- 2026-03-29: ユーザー判断で Phase 5 を完了扱いとしてクローズ。

## 完了条件

- 本番 URL（`https://xxxx.onrender.com`）でアプリが閲覧できる
- フロント画面・地図・API フィルタが正常に動作する
- GitHub Actions が定期的に実行され、スクレイパーが動作している
- 本番 DB のデータが定期的に更新されている
