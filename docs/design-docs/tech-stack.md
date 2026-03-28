# 技術スタック選定

**ステータス**: ✅ Active
**日付**: 2026-03-28
**決定者**: 人間

---

## 背景

首都圏（1都3県）の将棋大会情報を、地図と日時で絞り込めるWebアプリを構築するにあたり、技術スタックを選定した。
既存の将棋大会スケジュールサイト（Blogspot）からデータを自動取得し、地図UIで視覚的に探せることが要件。

---

## 検討した選択肢と決定

### 開発環境: devcontainer

**検討**: uv のみ（ローカル venv）vs devcontainer

**決定**: devcontainer

**理由**:
- エージェント（Claude Code等）に実装を任せる頻度が高い → コンテナが安全な実行境界になる
- マシンを変えても環境が一切崩れない
- GitHub Codespaces にも対応できる

### 依存管理: uv

**検討**: requirements.txt vs uv

**決定**: uv

**理由**:
- `venv` + `pip` + ロックファイルが1ツールで完結
- `uv.lock` をコミットすることでコンテナ内外の再現性を保証
- `requirements.txt` はバージョン固定の管理が手動で漏れやすい

### フロントエンド: 生HTML + Vanilla JS（Vue.js を不採用）

**検討**: Vue.js 3 vs 生HTML + Vanilla JS

**決定**: 生HTML + Vanilla JS

**理由**:
- 状態管理は「エリア選択」「日付レンジ」の2変数のみで、フレームワークが解決する複雑さがない
- Leaflet.js は独自のイベント・DOM操作を持つため、Vueと組み合わせると干渉リスクがある
- Vue.js を採用するとNode.js / npm / ビルド設定が必要になり、複雑さに対してリターンが小さい
- UIの複雑さが増した時点でフレームワーク導入を再検討する（`docs/design-docs/index.md` に記録する）

### 地図ライブラリ: Leaflet.js

**検討**: Leaflet.js vs Google Maps API

**決定**: Leaflet.js

**理由**:
- 無料・OSS。Google Maps APIは無料枠を超えると課金が発生する
- 都道府県ポリゴン（GeoJSON）との組み合わせが容易

### バックエンド: Python / FastAPI

**検討**: FastAPI vs Flask

**決定**: FastAPI

**理由**:
- Python はレビューしやすい（オーナーの主要言語）
- FastAPI は型安全・自動ドキュメント生成・非同期対応でFLaskより開発効率が高い

### スクレイピング: requests + BeautifulSoup4

**決定**: requests + BeautifulSoup4

**理由**:
- 対象サイト（Blogspot）は静的HTMLのためSeleniumは不要
- シンプルで十分。サイト構造変更時のデバッグも容易

### ジオコーディング: Nominatim (OpenStreetMap)

**検討**: Nominatim vs Google Geocoding API

**決定**: Nominatim

**理由**:
- 無料・OSS
- レートリミット（1 req/sec）があるがDBキャッシュで初回以降は不要
- 会場名の精度が低いケースはキャッシュに手動補正フィールドを設けて対応する

### データベース: SQLite

**検討**: SQLite vs PostgreSQL

**決定**: SQLite

**理由**:
- 大会データは書き込み頻度が低く（スクレイピング時のみ）、SQLiteの同時書き込み制限は問題にならない
- ファイル1個で完結する運用の軽さを優先

### スケジューラ: APScheduler

**決定**: APScheduler

**理由**:
- Pythonプロセス内で完結。外部cronサービス不要
- FastAPIとの統合が容易

### ホスティング: Vercel（フロント）+ Render または Fly.io（バックエンド）

**決定**: 無料枠のあるPaaS（**暫定。変更の可能性あり**）

**理由**:
- 個人プロダクトのため運用コストを最小化
- CI/CD連携が標準で提供される

> **注意**: ホスティング先は未確定。要件・コスト・運用負荷によって変更する可能性がある。
> 変更した場合はこのドキュメントと `ARCHITECTURE.md` を同じPRで更新すること。

---

## 影響

- `src/frontend/` は生HTMLのためビルドステップが不要
- `src/scraper/` はNominatimのレートリミットを考慮し、初回ジオコーディング結果を必ずキャッシュする
- Blogspotのサイト構造変更でスクレイパーが壊れるリスクがある → スクレイピング失敗時のアラート機構を設ける
