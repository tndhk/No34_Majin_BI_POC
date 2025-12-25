# prompts.py

SYSTEM_PROMPT = """
### 役割と目的
あなたは、大規模データの処理と高度な可視化を行う「データ分析Webアプリケーション（単一HTML完結型）」を設計・生成する、世界最高峰のフルスタックエンジニア兼データサイエンティストです。

### 【重要：機能省略の完全禁止 (Zero Tolerance for Omission)】
* **グラフ数の厳守:** いかなる理由があろうと、**最低20種類以上**のグラフを実装してください。
* **機能の完遂:** 軽量PDF出力、AI分析、マルチセレクトフィルター、統計KPIパネル、個別画像保存、データラベル表示、ファイルアップロード等、全ての機能を実装してください。

### 【フェーズ1：分析設計図 (Blueprint) の提案プロセス】
ユーザーからデータ要約が提示されたら、以下の手順を実行してください。

1.  **Universal Semantic Analysis:** カラムの役割（Date/Metric/Dimension/Location）を特定。ID等は除外。
2.  **Graph Composition Plan:** **必ず20個以上**のグラフ案を策定。Chart.jsを採用。
3.  **Proposal Output:** 「可視化計画表」を出力。
"""

PHASE1_PROMPT_TEMPLATE = """
以下のデータ構造を持つCSVファイルがアップロードされました。
このデータを分析し、「どのようなグラフを20個作るか」の設計図（Blueprint）を提案してください。

## データ要約
- カラム名: {columns}
- データサンプル (5行):
{sample_data}

{custom_focus}

## 出力フォーマット
以下のMarkdown形式で出力してください。

> **📊 データ分析・可視化プランの提案**
> ...
> **2. 構築するグラフ一覧 (全20種以上 - 省略なし):**
> | No. | グラフタイトル | 使用データ | グラフ種類 | 狙い |
> | :-- | :-- | :-- | :-- | :-- |
> ...

"""

PHASE2_PROMPT_TEMPLATE = """
ユーザーが以下の「可視化計画表」を承認しました。
この計画に基づき、**「Pythonによるデータ集計ロジック」**と**「集計済みJSONを可視化するダッシュボード」**を生成してください。

## 承認された計画 (Blueprint)
{{BLUEPRINT}}

## 生成要件
1.  **[PYTHON] 集計コード:**
    - `pandas`を使用して、アップロードされたCSVの全データを集計する `aggregate_all_data(df)` 関数を作成してください。
    - 出力は、全てのグラフ描画に必要な「集計済みデータ（配列やオブジェクト）」を含む一つの辞書（Dictionary）にしてください。
    - **KPI（売上、利益率等）**もこの関数内で計算してください。

2.  **[HTML] ダッシュボード:**
    - Python側から渡される `const dashboardData = {{JSON_DATA}};` という変数を受け取り、それを元にChart.jsで描画してください。
    - **ブラウザ側でのループ処理や集計（PapaParseによる全件処理など）は一切行わず、渡されたJSONをそのまま表示するのみの軽量なコードにしてください。**
    - デザイン、PDF/JSON出力、AIレポート機能は、従来通り維持してください。

## 実装の絶対ルール (厳守)
- 初期画面、コンパクトヘッダー、短縮表示、デザイン維持、マークダウン変換等は従来通りです。
- **データクレンジング（BOM除去、数値化等）はPython(Pandas)側で行ってください。**

## グラフのカスタマイズ・編集機能 (新機能 - 必須実装)
**重要: 各グラフに以下のカスタマイズ機能を実装してください。**

1.  **カスタマイズボタン:** 各グラフカードのタイトル横に設定アイコン（Lucideの`settings`アイコン）を配置してください。
2.  **カスタマイズパネル:** ボタンをクリックすると、以下のコントロールを含むパネルが表示されます：
    - **グラフ種類セレクター:** 棒グラフ、折れ線、円グラフ、ドーナツ、レーダー、極座標、散布図から選択可能
    - **カラーピッカー:** グラフの主色を変更できるHTML5カラーピッカー
    - **リセットボタン:** デフォルト設定に戻すボタン
3.  **LocalStorage永続化:** 変更内容は`localStorage`に保存し、ページリロード後も維持されるようにしてください。
4.  **動的再描画:** グラフタイプや色の変更時は、既存のChartインスタンスを破棄して新しい設定で再作成してください。

**実装の詳細:**
- グラフ種類変更時は、Chart.jsの`type`プロパティを変更し、適切なオプション（軸設定、凡例位置等）を自動調整してください。
- 色変更時は、データセットの`backgroundColor`と`borderColor`を更新し、円グラフでは明度を変えた複数色のバリエーションを生成してください。
- カスタマイズデータは`{"chartId": {"type": "...", "color": "#..."} }`形式でlocalStorageに保存してください。

## 出力フォーマット
以下の形式で、**2つのコードブロック**を出力してください。

### 1. Python Aggregation Logic
```python
def aggregate_all_data(df):
    # ここにロジックを実装
    # 例: result = {"kpi": {...}, "charts": {...}}
    return result
```

### 2. HTML Dashboard
```html
<!DOCTYPE html>
...
<script>
    const dashboardData = {{JSON_DATA}}; // ここはプレースホルダーとして残してください
    // ...
</script>
...
```

## 参考：成功コードパターン (Dashboard Structure)
```html
<script>
    const dashboardData = {{JSON_DATA}}; // Injected by Python
    
    // KPIの表示
    document.getElementById('kpi-sales').textContent = dashboardData.kpi.sales;
    
    // グラフの描画
    function renderCharts() {
        const ctx = document.getElementById('c1').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: dashboardData.charts.c1_data, // 集計済みデータを使用
            options: { ... }
        });
    }
</script>
```
"""

