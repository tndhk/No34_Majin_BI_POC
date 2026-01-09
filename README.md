# 🧞‍♂️ Majin式 GemBI Generator (Local Edition)

**Majin式 GemBI Generator** は、CSVデータをアップロードするだけで、高度なデータ分析ダッシュボード（HTML形式）を自動生成するローカルアプリケーションです。
Gemini 2.0 (or Pro) を活用し、[majin式GemBI.md](majin式GemBI.md) で定義された厳格なデータVisualization手法に基づいて、分析設計からコーディングまでを全自動で行います。

## ✨ 特徴

- **ハイブリッド生成アーキテクチャ (Performance Optimized)**:
  - **Python (Pandas)**: サーバーサイド（Streamlit）で全データのパースと集計を高速実行。
  - **JSON Injection**: 集計結果のみをHTMLに注入。
  - **Lightweight Frontend**: ブラウザは描画のみに専念するため、数万行のデータでも快適に表示可能。
- **2段階生成フロー**:
  1.  **Blueprint Phase**: データを分析し、「どのようなグラフを20個作るか」の設計図を提案します。
  2.  **Coding Phase**: 承認された設計図に基づき、Python集計コードとダッシュボードHTMLを生成します。
- **Direct View モード**:
  - 生成後、スプラッシュ画面をスキップして即座にダッシュボードを表示します。
- **グラフのカスタマイズ・編集機能 (NEW)**:
  - 各グラフのタイトル横にある設定アイコンをクリックすることで、グラフの種類（棒グラフ、折れ線、円グラフ、ドーナツ、レーダー、極座標、散布図）と色を自由にカスタマイズできます。
  - カスタマイズ設定はブラウザのLocalStorageに保存され、ページをリロードしても維持されます。
  - リセットボタンで元のデフォルト設定に戻すことも可能です。

## 🛠 動作環境

- **OS**: Mac / Windows / Linux
- **Python**: 3.10 以上
- **Google API Key**: Gemini APIを利用できるキーが必要です。

## 🚀 インストール & セットアップ

1.  **リポジトリのクローン (またはディレクトリ移動)**

    ```bash
    cd /path/to/majin_bi
    ```

2.  **仮想環境の作成**

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # Mac/Linux
    # .venv\Scripts\activate   # Windows
    ```

3.  **依存ライブラリのインストール**

    ```bash
    pip install -r requirements.txt
    ```

4.  **環境設定**
    `.env.example` を `.env` にリネームし、APIキーを設定してください（アプリ起動後の画面入力も可能です）。
    ```bash
    cp .env.example .env
    ```

## 🎮 使い方

1.  **アプリケーションの起動**

    ```bash
    streamlit run app_v2.py
    ```

    自動的にブラウザが開き、アプリが起動します。

2.  **生成フロー**
    - **Step 1**: 分析したいCSVファイルをアップロードします（日本語ヘッダー対応）。
    - **Step 2**: 「🚀 Generate Blueprint」をクリックし、AIが提案するグラフ構成案を確認します。
    - **Step 3**: 内容に問題なければ「✨ Generate Application Code」をクリックします。
    - **完了**: 生成されたHTMLファイルをダウンロードして、ブラウザで開いてください。

## 📂 生成されるダッシュボードについて

ダウンロードしたHTMLファイル（`majin_analytics_dashboard.html`）は、インターネット接続があればどこでも動作します。
ダッシュボード内の「AI戦略分析レポート」機能を使用するには、HTMLファイル内のソースコードにAPIキーを埋め込むか（推奨されません）、実行時にブラウザのコンソール等から渡す必要があります（※生成元のアプリ設定により、現在はAPIキー空欄で出力されます）。

## 📝 ライセンス

Private / Internal Use Only
