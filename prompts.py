# prompts.py

SYSTEM_PROMPT = """
### 役割と目的
あなたは、大規模データの処理と高度な可視化を行う「データ分析Webアプリケーション（単一HTML完結型）」を設計・生成する、世界最高峰のフルスタックエンジニア兼データサイエンティストです。

### 【重要：機能省略の完全禁止 (Zero Tolerance for Omission)】
* **グラフ数の厳守:** いかなる理由があろうと、**最低20種類以上**のグラフを実装してください。
* **機能の完遂:** 軽量PDF出力、AI分析、マルチセレクトフィルター、統計KPIパネル、個別画像保存、データラベル表示、ファイルアップロード等、全ての機能を実装してください。

### 【重要：Pythonグラフライブラリ使用禁止】
* **可視化はChart.js（フロントエンド）のみ:** plotly, matplotlib, seaborn, altair等のPythonグラフライブラリは一切使用禁止。
* **Python側は集計のみ:** Pandasでデータ集計を行い、JSON形式で出力。描画はHTML/Chart.jsで行う。

### 【フェーズ1：分析設計図 (Blueprint) の提案プロセス】
ユーザーからデータ要約が提示されたら、以下の手順を実行してください。

1.  **Universal Semantic Analysis:** カラムの役割（Date/Metric/Dimension/Location）を特定。ID等は除外。
2.  **Graph Composition Plan:** **必ず20個以上**のグラフ案を策定。Chart.jsを採用。
3.  **Proposal Output:** 「可視化計画表」を出力。
"""

# ═══════════════════════════════════════════════════════════════════════════════
# MAJIN ORACLE DESIGN SYSTEM
# Mystical Dark Theme with Glowing Accents
# ═══════════════════════════════════════════════════════════════════════════════

DESIGN_SYSTEM = """
## デザインシステム：Majin Executive (信頼と知性のDeep Navyテーマ)

### コンセプト
「ゲーミング」ではなく「エグゼクティブ・プロフェッショナル」。
深みのあるネイビーとスレートグレーを基調とし、高い可読性（コントラスト）と信頼感を演出する。
過度な発光（Glow）は抑え、洗練されたボーダーとシャドウで階層を表現する。

### カラーパレット（厳守）
```css
/* ベースカラー - Deep Executive Navy */
--void-deep: #0b1120;       /* Dark Midnight Blue (背景最下層) */
--void-surface: #151e32;    /* Deep Slate (メイン背景) */
--void-elevated: #1e293b;   /* Slate 800 (カード背景) */
--void-border: #334155;     /* Slate 700 (明確な境界線) */

/* アクセントカラー - Professional Trust */
--oracle-primary: #38bdf8;   /* Sky 400 (プライマリアクセント・信頼) */
--oracle-primary-dim: #0284c7; /* Sky 600 */
--oracle-gold: #fbbf24;      /* Amber 400 (ハイライト・洞察) */
--oracle-gold-dim: #d97706;  /* Amber 600 */
--oracle-accent: #818cf8;    /* Indigo 400 (二次アクセント) */
--oracle-success: #34d399;   /* Emerald 400 (ポジティブ) */
--oracle-danger: #f87171;    /* Red 400 (ネガティブ) */

/* テキストカラー（高コントラスト） */
--text-primary: #f8fafc;     /* Slate 50 (ほぼ白・最高可読性) */
--text-secondary: #cbd5e1;   /* Slate 300 (補足情報・高可読性) */
--text-muted: #94a3b8;       /* Slate 400 (控えめな情報) */

/* エフェクト */
--shadow-card: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.15);
--shadow-elevated: 0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -2px rgba(0, 0, 0, 0.2);
```

### グラフカラーパレット (Executive Suite)
Chart.jsで使用する色の配列（落ち着いたトーン、しかし識別しやすい）:
```javascript
const ORACLE_COLORS = [
    '#38bdf8',  // Sky 400 (Primary)
    '#fbbf24',  // Amber 400 (Secondary)
    '#818cf8',  // Indigo 400
    '#34d399',  // Emerald 400
    '#f472b6',  // Pink 400
    '#2dd4bf',  // Teal 400
    '#a78bfa',  // Violet 400
    '#fb923c',  // Orange 400
    '#9ca3af',  // Gray 400
    '#60a5fa',  // Blue 400
];
```

### フォント設定
```css
/* Google Fontsからインポート */
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=DM+Sans:wght@400;500;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* 適用 */
font-family-display: 'Cormorant Garamond', Georgia, serif;  /* 威厳ある見出し */
font-family-body: 'DM Sans', system-ui, sans-serif;         /* 現代的で読みやすい本文 */
font-family-mono: 'JetBrains Mono', monospace;              /* 正確な数値表現 */
```
"""

PHASE1_PROMPT_TEMPLATE = """
以下のデータ構造を持つCSVファイルがアップロードされました。
このデータを分析し、「エグゼクティブが意思決定に使える」高度なグラフを20個設計してください。

## データ要約
- カラム名: {columns}
- データサンプル (5行):
{sample_data}

## 出力フォーマット
以下のMarkdown形式で出力してください。

> **📊 Executive Insight Plan**
> ...
> **2. Visualization Strategy (All 20 Charts):**
> | No. | Chart Title | Data Used | Chart Type | Executive Insight (狙い) |
> | :-- | :-- | :-- | :-- | :-- |
> ...

"""

PHASE2_PROMPT_TEMPLATE = """
ユーザーが以下の「可視化計画表」を承認しました。
この計画に基づき、**「Pythonによるデータ集計ロジック」**と**「集計済みJSONを可視化するダッシュボードHTML」**を生成してください。

## 承認された計画 (Blueprint)
{{BLUEPRINT}}

## 生成要件
1.  **[PYTHON] 集計コード:**
    - `pandas`を使用して、アップロードされたCSVの全データを集計する `aggregate_all_data(df)` 関数を作成してください。
    - 出力は、全てのグラフ描画に必要な「集計済みデータ（配列やオブジェクト）」を含む一つの辞書（Dictionary）にしてください。
    - **KPI（売上、利益率等）**もこの関数内で計算してください。
    - **【必須】Micro-Insights:** 各グラフに対応する短いインサイト（40文字程度の1文）を `micro_insights` 辞書として生成してください。
      例: `"micro_insights": {"chart_1": "A地域が売上の40%を占め主力市場", "chart_2": "週末の売上が平日比1.5倍", ...}`
    - **【必須】Global Summary:** データ全体の総括を `global_summary` 文字列として生成してください（100-150文字程度）。
    - **【重要】型安全性とエラー防止:**
        - **`.cat` アクセサの使用は禁止**します。カテゴリ変数は必ず文字列型として扱い、`.unique()` や `.value_counts()` を使用してください。
        - **`.dt` アクセサ**を使用する場合、事前に対象カラムを `pd.to_datetime()` で確実に日時型に変換してください。

2.  **[HTML] ダッシュボード (Majin Executive Theme):**
    - Python側から渡される `const dashboardData = {{JSON_DATA}};` を受け取り、Chart.jsで描画してください。
    - **ブラウザ側での重い集計処理は禁止です。**
    - **デザインシステム（Majin Executive）を厳守してください。**
    - **【必須】Micro-Insights表示:** 各グラフカードのタイトル下に `.micro-insight` ボックスを配置し、`dashboardData.micro_insights` から対応するテキストを表示してください。
      スタイル例: `background: rgba(56,189,248,0.1); border-left: 3px solid var(--oracle-primary); padding: 0.5rem 0.75rem; font-size: 0.85rem; color: var(--text-secondary);`
    - **【必須】Global Summary表示:** KPIセクション直下（グラフ一覧の上、ダッシュボード最上部付近）に `.global-summary` セクションを配置し、`dashboardData.global_summary` を表示してください。目立つデザインで、データ全体の概要を一目で把握できるようにしてください。
    - **【重要】JavaScript安全性 (Null Safety):**
        - `dashboardData` や `dashboardData.charts`、`dashboardData.micro_insights` へのアクセス時は、必ず存在チェックを行ってください。
        - `Object.keys()` を使用する際は、`Object.keys(data.charts || {})` のように空オブジェクトへのフォールバックを実装し、`TypeError` を防いでください。
        - `getChartData` などの主要関数内では `try-catch` を使用し、一部のデータ欠損で全体が停止しないようにしてください。

## ═══════════════════════════════════════════════════════════════════════════
## 【最重要】デザインシステム：Majin Executive
## 信頼と知性のDeep Navy/Slateテーマを実装してください
## ═══════════════════════════════════════════════════════════════════════════

### 必須CSSカスタムプロパティ
```css
:root {
    --void-deep: #0b1120;
    --void-surface: #151e32;
    --void-elevated: #1e293b;
    --void-border: #334155;
    --oracle-primary: #38bdf8;
    --oracle-gold: #fbbf24;
    --oracle-accent: #818cf8;
    --text-primary: #f8fafc;
    --text-secondary: #cbd5e1;
    --shadow-card: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
}
```

### 必須フォント
```html
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=DM+Sans:wght@400;500;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

### 必須スタイルルール

1.  **背景**:
    `body { background-color: var(--void-deep); color: var(--text-primary); }`
    ※グラデーションは最小限にし、フラットで読みやすい背景を維持。

2.  **カード（Chart Container）**:
    ```css
    .card {
        background: var(--void-elevated);
        border: 1px solid var(--void-border); /* 明確な境界線 */
        border-radius: 0.75rem;
        box-shadow: var(--shadow-card);
        padding: 1.5rem;
    }
    ```

3.  **タイポグラフィ**:
    - 見出し (H1-H3): `font-family: 'Cormorant Garamond', serif; letter-spacing: 0.02em;`
    - 本文/ラベル: `font-family: 'DM Sans', sans-serif; color: var(--text-secondary);`
    - 数値: `font-family: 'JetBrains Mono', monospace; font-weight: 500;`

4.  **Chart.js設定 (可読性最優先)**:
    ```javascript
    Chart.defaults.color = '#cbd5e1';  // Slate 300 (はっきり見える色)
    Chart.defaults.borderColor = '#334155'; // Slate 700 (グリッド線)
    Chart.defaults.font.family = "'DM Sans', sans-serif";
    ```

5.  **ボタン・UI**:
    - プライマリボタン: `background: linear-gradient(to right, #0ea5e9, #2563eb);` (Sky to Blue)
    - 角丸は少し小さめ(0.5rem)で、シャープな印象に。

### 禁止事項
- **黒背景(#000)の使用禁止**: 必ず `--void-deep` (#0b1120) を使用。
- **過度なGlow効果の禁止**: ぼやけた光彩よりも、明確なコントラストを優先。
- **可読性の低い文字色**: 暗いグレーや青色文字は禁止。必ず `#cbd5e1` 以上明るい色を使用。

## グラフのカスタマイズ・編集機能 (新機能 - 必須実装)
**重要: 各グラフに以下のカスタマイズ機能を実装してください。**

1.  **カスタマイズボタン:** 各グラフカードのタイトル横に設定アイコン（Lucideの`settings`アイコン）を配置してください。
2.  **カスタマイズパネル:** ボタンをクリックすると、以下のコントロールを含むパネルが表示されます：
    - **グラフ種類セレクター:** 棒グラフ、折れ線、円グラフ、ドーナツ、レーダー、極座標、散布図から選択可能
    - **カラーピッカー:** グラフの主色を変更できるHTML5カラーピッカー
    - **リセットボタン:** デフォルト設定に戻すボタン
3.  **LocalStorage永続化:** 変更内容は`localStorage`に保存し、ページリロード後も維持されるようにしてください。
4.  **動的再描画:** グラフタイプや色の変更時は、既存のChartインスタンスを破棄して新しい設定で再作成してください。

## 出力フォーマット
以下の形式で、**2つのコードブロック**を出力してください。

### 1. Python Aggregation Logic
```python
def aggregate_all_data(df):
    # ...
    return result
```

### 2. HTML Dashboard (Majin Executive Theme)
```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <!-- ... CSS, Fonts ... -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        // Chart.js Default Settings (Global)
        Chart.defaults.color = '#cbd5e1';
        Chart.defaults.borderColor = '#334155';
        Chart.defaults.font.family = "'DM Sans', sans-serif";

        // Executive Palette
        const ORACLE_COLORS = [
            '#38bdf8', '#fbbf24', '#818cf8', '#34d399', '#f472b6',
            '#2dd4bf', '#a78bfa', '#fb923c', '#9ca3af', '#60a5fa'
        ];

        // 【必須】カラー適用ヘルパー関数
        function assignOracleColors(chartData, index) {
            const color = ORACLE_COLORS[index % ORACLE_COLORS.length];
            chartData.datasets.forEach(ds => {
                // Pie/Doughnutの場合はパレット全体を使用
                if (ds.type === 'pie' || ds.type === 'doughnut' || !ds.type && chartData.labels.length > 1) {
                    ds.backgroundColor = ORACLE_COLORS;
                    ds.borderColor = '#1e293b'; // 背景色と同じで境界を目立たなくする
                } else {
                    // Bar/Line等は単色
                    ds.backgroundColor = color;
                    ds.borderColor = color;
                }
            });
            return chartData;
        }
    </script>
</head>
<body>
    <!-- ... Dashboard Content ... -->
    <script>
        // ...
        // グラフ描画ループ内で必ず: assignOracleColors(data, i) を呼ぶこと
        // ...
    </script>
</body>
</html>
```
"""

