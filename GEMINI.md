# Project Context: Majin式 GemBI Generator (Local Edition)

## Project Overview
**Majin式 GemBI Generator** は、CSVデータから高度なデータ分析ダッシュボードを自動生成するStreamlitアプリケーションです。Gemini 2.0 APIを活用し、「majin式GemBI.md」で定義された厳格なVisualization手法（Majin式）に基づいて、分析設計（Blueprint）からコーディングまでを自動化します。

### 核心機能
*   **ハイブリッド生成アーキテクチャ:** サーバーサイド（Python/Pandas）で高速にデータ集計を行い、フロントエンド（HTML/Chart.js）で軽量・高速な描画を実現。
*   **2段階生成フロー:**
    1.  **Blueprint Phase:** AIがデータを分析し、20個以上のグラフ設計図を提案。
    2.  **Coding Phase:** 承認された設計図に基づき、Python集計コードとダッシュボードHTMLを生成。
*   **対話型分析:** 生成後のダッシュボードに対し、AIチャットを通じて深掘り分析や追加グラフ生成が可能。
*   **Majin Oracle デザインシステム:** 深淵の闇（#06060a）をベースに、神秘的なアクセント色（Oracle Cyan, Gold, Purple）とグロー効果を多用した独特のUI。

## 実行・管理コマンド

### アプリケーションの起動
本プロジェクトのメインエントリポイントは `app_v2.py` です。

#### 標準的な起動
```bash
# 仮想環境を有効化している場合
streamlit run app_v2.py

# パスを直接指定する場合（確実）
.venv/bin/streamlit run app_v2.py
```

#### バックグラウンドでの永続実行 (CLI推奨)
サーバーを落とさずにバックグラウンドで動かし続ける場合は、`nohup` を使用します。
```bash
nohup .venv/bin/streamlit run app_v2.py > .gemini/tmp/streamlit_v2.log 2>&1 &
```
※ 起動状態の確認: `pgrep -f "streamlit run app_v2.py"`

### 品質管理・テスト
```bash
# テスト・カバレッジ
pytest
pytest --cov=src --cov-report=html
```

## アーキテクチャ & データフロー

### ディレクトリ構造
*   `app_v2.py`: エントリポイント（UI & オーケストレーション）
*   `prompts.py`: AIプロンプト定義（SYSTEM_PROMPT, DESIGN_SYSTEM等）
*   `src/services/`: ビジネスロジック
    *   `ai_generator.py`: Blueprint/コード生成
    *   `chat_handler.py`: 対話型分析処理
    *   `data_processor.py`: Pandasによる集計
*   `docs/SPECIFICATION.md`: 詳細仕様書

### パフォーマンス制約
*   **生成時間:** ダッシュボード 60秒以内 / 追加グラフ 10秒以内
*   **応答時間:** チャット 5秒以内
*   **対応サイズ:** 最大100MB / 100万行

## 開発・コーディングルール

### タスク分類と対応
*   **🟢 軽量 (Lightweight):** 数行の変更。即実装し、1-2文で報告。
*   **🟡 標準 (Standard):** 複数ファイル、機能追加。3-7項目のチェックリスト提示 → 実装 → Lint確認 → 要約報告。
*   **🔴 重要 (Critical):** アーキテクチャ、セキュリティ、DB変更。`create_plan`による承認フロー必須。

### テスト戦略 (.agent/rules/test.md)
1.  **テスト観点表の作成:** Case ID, 入力/前提条件, 観点, 期待結果 を整理。
2.  **境界値分析:** 0, min, max, ±1, empty, NULL 等を網羅。
3.  **失敗系重視:** 異常系テストを正常系と同数以上実装。
4.  **Given/When/Then:** 各テストケースに明記。
5.  **カバレッジ:** ブランチカバレッジ100%を目標とする。

### AIプロンプトの維持
*   `prompts.py` 内の `DESIGN_SYSTEM` を厳守すること。
*   グラフ数は**最低20種類以上**を維持（Zero Tolerance for Omission）。
*   PDF出力、フィルター、統計KPI、画像保存等の全機能を実装に含めること。

## セキュリティ
*   APIキーは `.env` で管理。
*   生成されたHTML内にはAPIキーを埋め込まない（空欄で出力）。