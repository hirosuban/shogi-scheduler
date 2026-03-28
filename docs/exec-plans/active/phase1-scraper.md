# Phase 1: スクレイパー

## 目標

Blogspotの将棋大会スケジュールサイトから首都圏の大会情報を自動取得し、
緯度経度付きでSQLiteに保存するパイプラインを構築する。

## 背景・動機

フロントエンドとAPIの基盤となるデータが必要。
データが取れなければ後続フェーズは進められないため、最初に着手する。

## アプローチ

1. 対象ページのHTMLを `requests` で取得、`BeautifulSoup4` でパース
2. 都道府県情報を判定し、首都圏（東京・神奈川・埼玉・千葉）のみ抽出
3. 会場名を `Nominatim` でジオコーディング → lat/lng取得
4. 結果をSQLiteに保存（ジオコーディング結果をキャッシュ）
5. `APScheduler` で定期実行（頻度は週1〜日1で要検討）

## タスク

- [ ] `.devcontainer/` セットアップ（Python環境・uv・必要なVS Code拡張の定義）
- [ ] `pyproject.toml` 作成・依存パッケージ追加（`uv add` で管理）、`uv.lock` をコミット
- [ ] `src/scraper/` ディレクトリ作成
- [ ] Blogspotページ構造の解析・パーサー実装
- [ ] 首都圏フィルタリングロジック実装（都道府県判定）
- [ ] SQLiteスキーマ設計・マイグレーション実装
  - テーブル: `tournaments`（id, date, name, venue, prefecture, lat, lng, category, source_url）
  - テーブル: `geocode_cache`（venue_name, lat, lng, updated_at）
- [ ] Nominatimジオコーディング実装（キャッシュ参照 → APIコール → キャッシュ保存）
- [ ] スクレイピング失敗時のアラート機構（ログ出力 + 構造変化の検出）
- [ ] APSchedulerによる定期実行設定
- [ ] ローカルでの動作確認（実データで取得・保存が正常に動くこと）

## 意思決定ログ

- Nominatimはレートリミット（1 req/sec）があるため、`geocode_cache` テーブルで初回以降はAPIコールをスキップする
- 会場名のジオコーディング精度が低いケースは `geocode_cache` に手動補正フィールドを設けて対応する
- Seleniumは不要（対象サイトは静的HTML）

## 完了条件

- 首都圏の大会データがSQLiteに保存されていること
- 各レコードに lat/lng が付与されていること（取得失敗分は NULL 許容）
- 定期実行が設定され、2回以上の自動取得が正常に動作すること
