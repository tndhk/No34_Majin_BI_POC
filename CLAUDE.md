# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

Majin式 GemBI Generator は、CSVデータから高度なデータ分析ダッシュボードを自動生成するStreamlitアプリケーション。Gemini 2.0 APIを活用し、「majin式GemBI.md」で定義された厳格なVisualization手法に基づいて、Blueprint設計とコード生成を自動化する。

核心機能:
- ハイブリッド生成アーキテクチャ: サーバーサイド（Python/Pandas）で集計、フロントエンド（HTML/Chart.js）で描画
- 2段階生成フロー: Blueprint Phase（グラフ設計20個）→ Coding Phase（Python集計 + HTML生成）
- 対話型分析: AIチャットによる深掘り分析と追加グラフ生成（docs/SPECIFICATION.md参照）

## 開発コマンド

### セットアップ
```bash
# 仮想環境作成・有効化
python3 -m venv .venv
source .venv/bin/activate  # Mac/Linux
# .venv\Scripts\activate   # Windows

# 依存関係インストール
pip install -r requirements.txt

# 環境設定（APIキーを.envに設定）
cp .env.example .env
```

### アプリケーション実行
```bash
# アプリ起動
streamlit run app_v2.py
```

### テスト・品質チェック
```bash
# テスト実行（全体）
pytest

# カバレッジ計測
pytest --cov=src --cov-report=html

# 特定テストファイル実行
pytest tests/test_performance.py

# Linting（Ruff）
ruff check .
ruff check --fix .  # 自動修正

# Formatting
ruff format .

# 型チェック（mypy）
mypy src/

# pre-commit実行
pre-commit run --all-files
```

## アーキテクチャ

### ディレクトリ構造
```
.
├── app_v2.py             # メインアプリケーション（Streamlit UI + オーケストレーション）
├── prompts.py            # AIプロンプト定義（SYSTEM_PROMPT, DESIGN_SYSTEM等）
├── src/
│   ├── services/         # ビジネスロジック層
│   │   ├── ai_generator.py      # AIを使ったダッシュボード生成
│   │   ├── chat_handler.py      # 対話型分析ハンドラー
│   │   └── data_processor.py    # データ処理・集計
│   └── utils/            # ユーティリティ関数
├── tests/                # pytest テストスイート
│   ├── conftest.py       # テストフィクスチャ
│   ├── test_performance.py  # パフォーマンステスト
│   └── services/         # サービス層のテスト
└── docs/                 # ドキュメント
    └── SPECIFICATION.md  # 機能仕様書（対話型分析の詳細）
```

### データフロー

#### ワンショット生成
1. CSV Upload → Pandas読み込み（エンコーディング自動判定）
2. AI Blueprint生成（AIGenerator.generate_blueprint） → 20+グラフの設計図提案
3. AI Code生成（AIGenerator.generate_dashboard_code） → Python集計コード + HTMLダッシュボード
4. Python実行（aggregate_all_data） → JSON生成
5. HTML組み立て → JSON注入 + Direct View Shim追加
6. Dashboard表示 + Chat初期化

#### 対話型分析（docs/SPECIFICATION.md参照）
1. User Input → Context構築（データサマリー + 会話履歴）
2. ChatHandler.handle_message → 意図分類（Intent: QUESTION/ADD_CHART/ANALYZE/SUMMARIZE）
3. 処理実行 → 回答生成/グラフ追加/分析計算
4. ChatResponse返却 → UI更新

### セッション状態（st.session_state）
- `csv_data`: 生CSVテキスト
- `df_full`: 全データ（DataFrame）
- `blueprint`: Blueprint（グラフ構成案）
- `aggregated_data`: 集計済みデータ（JSON）
- `dashboard_html`: 生成されたHTML
- `chat_history`: 会話履歴（list）
- `generation_status`: 生成状態（"idle" | "generating" | "complete"）

## 重要な設計原則

### AIプロンプト設計（prompts.py）
- `SYSTEM_PROMPT`: Blueprint/Code生成の基本指示
- `DESIGN_SYSTEM`: Majin Oracleデザインシステム（ダークテーマ、カラーパレット）
- グラフ数は**最低20種類以上**を厳守（Zero Tolerance for Omission）
- 全機能実装（PDF出力、AI分析、フィルター、統計KPI、画像保存等）

### パフォーマンス制約（docs/SPECIFICATION.md §5.1）
- ダッシュボード生成: 60秒以内
- チャット応答: 5秒以内
- 追加グラフ生成: 10秒以内
- 対応データサイズ: 100MB / 100万行まで

### Majin Oracleデザインシステム
`prompts.py`内のDESIGN_SYSTEMで定義。深淵の闇ベース（--void-deep: #06060a）、神秘的なアクセント色（--oracle-cyan, --oracle-gold, --oracle-purple）、グロー効果を多用する独特のUIデザイン。

## コーディングルール（.agent/rules/）

### 基本方針（.agent/rules/coding.md）
- タスク分類: 🟢軽量（数行変更） / 🟡標準（複数ファイル） / 🔴重要（アーキテクチャ・セキュリティ）
- 🟢: 即実装、1-2文で報告
- 🟡: 3-7項目のチェックリスト提示 → 実装 → lint確認 → 要約報告
- 🔴: `create_plan` → 承認待ち → 段階実行
- 日本語で回答（ユーザー指示に従う）

### テスト戦略（.agent/rules/test.md）
1. テスト観点表を必ず作成（同値分割/境界値分析）
   - Columns: `Case ID`, `Input / Precondition`, `Perspective`, `Expected Result`, `Notes`
   - 境界値: 0 / minimum / maximum / ±1 / empty / NULL を網羅
2. 失敗系テストは成功系と同数以上実装
3. Given/When/Thenコメントを各テストケースに記述
4. 例外検証では型とメッセージを明示的に確認
5. ブランチカバレッジ100%を目標（達成困難時は影響範囲を文書化）

### ツール使用方針
- 並列実行推奨: read_file/grep/codebase_search等の読み取り専用ツールは`multi_tool_use.parallel`で実行
- web_search: 外部サービス最新仕様、バージョン依存動作、エラーメッセージ調査時に積極活用
- read_lints: 変更後に実行し、修正可能なエラーは即座に対処

## Git & CI/CD

### CI（.github/workflows/*.yml）
- Python 3.10, 3.11, 3.12でマトリクステスト
- pre-commitフック実行（lint, format, 型チェック）
- ブランチ戦略: main（本番）, develop（開発）, feature/**, claude/**

### コミットメッセージ（.agent/rules/commit-message-format.md）
詳細は該当ファイル参照。簡潔で意図が明確なメッセージを記述。

## セキュリティ & 依存関係

- APIキー: `.env`で管理（`.env.example`をコピー）
- 本番HTML出力時はAPIキーを空欄で出力（セキュリティ考慮）
- Gemini API: `google-genai`パッケージ使用
  - 推奨モデル: `gemini-2.5-flash`（2026年1月時点の最新安定版）
  - 次世代: `gemini-3-flash-preview`（実験版）
  - 軽量版: `gemini-2.5-flash-lite`（高速・低コスト）
  - app_v2.pyのサイドバーで選択可能
- Streamlit: UI/UXフレームワーク
- Pandas: データ処理・集計エンジン

## 参考ドキュメント

- `majin式GemBI.md`: Visualization手法の詳細仕様（103KB、日本語）
- `docs/SPECIFICATION.md`: 機能仕様書（対話型分析フローの詳細）
- `README.md`: ユーザー向けインストール・使用方法
- `.agent/rules/`: コーディング/テスト/コミットの厳格なルール
