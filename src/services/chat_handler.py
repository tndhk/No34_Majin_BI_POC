"""
ChatHandler - AIチャットによる対話型分析

責務:
- ユーザーメッセージの意図分類
- 質問応答
- 追加グラフ生成リクエスト処理
- コンテキスト管理
"""

import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any

import pandas as pd


class Intent(Enum):
    """ユーザーの意図"""

    QUESTION = "question"  # データに関する質問
    ADD_CHART = "add_chart"  # グラフ追加リクエスト
    ANALYZE = "analyze"  # 分析リクエスト
    SUMMARIZE = "summarize"  # まとめリクエスト
    GENERAL = "general"  # 一般的な会話


@dataclass
class ChatResponse:
    """チャット応答"""

    type: str  # "text", "chart", "insight", "error"
    content: str
    chart_spec: dict[str, Any] | None = None
    chart_html: str | None = None
    data: dict[str, Any] | None = None


class ChatHandler:
    """AIチャットを処理するクラス"""

    def __init__(self, model):
        """
        Args:
            model: Gemini モデルインスタンス
        """
        self.model = model

    def classify_intent(self, message: str) -> Intent:
        """
        ユーザーメッセージの意図を分類する

        Args:
            message: ユーザーメッセージ

        Returns:
            Intent: 分類された意図
        """
        prompt = f"""
ユーザーのメッセージを以下のカテゴリに分類してください。

カテゴリ:
- question: データに関する質問（「〜は何？」「なぜ〜？」「どこが一番〜？」）
- add_chart: グラフ追加リクエスト（「〜を見せて」「グラフを追加」「可視化して」）
- analyze: 分析リクエスト（「分析して」「比較して」「相関を見て」）
- summarize: まとめリクエスト（「まとめて」「レポートにして」「要約して」）
- general: その他

ユーザーメッセージ: {message}

JSON形式で回答してください: {{"intent": "カテゴリ名", "entities": ["抽出されたエンティティ"]}}
"""
        response = self.model.generate_content(prompt)
        try:
            result = json.loads(response.text)
            intent_str = result.get("intent", "general")
            return Intent(intent_str)
        except (json.JSONDecodeError, ValueError):
            return Intent.GENERAL

    def handle_message(self, message: str, context: dict[str, Any]) -> ChatResponse:
        """
        ユーザーメッセージを処理して応答を生成する

        Args:
            message: ユーザーメッセージ
            context: コンテキスト情報（df, summaryなど）

        Returns:
            ChatResponse: 応答
        """
        intent = self.classify_intent(message)

        if intent == Intent.QUESTION:
            return self._handle_question(message, context)
        elif intent == Intent.ADD_CHART:
            return self._handle_add_chart(message, context)
        elif intent == Intent.ANALYZE:
            return self._handle_analyze(message, context)
        elif intent == Intent.SUMMARIZE:
            return self._handle_summarize(message, context)
        else:
            return self._handle_general(message, context)

    def _handle_question(self, message: str, context: dict[str, Any]) -> ChatResponse:
        """質問に対する応答を生成"""
        df = context.get("df")
        data_info = self._get_data_info(df) if df is not None else ""

        prompt = f"""
以下のデータに関する質問に答えてください。

## データ情報
{data_info}

## 質問
{message}

簡潔に回答してください（3-5文程度）。具体的な数値があれば含めてください。
"""
        response = self.model.generate_content(prompt)
        return ChatResponse(type="text", content=response.text)

    def _handle_add_chart(self, message: str, context: dict[str, Any]) -> ChatResponse:
        """グラフ追加リクエストを処理"""
        df = context.get("df")
        columns = df.columns.tolist() if df is not None else []

        prompt = f"""
以下のリクエストに基づいてグラフ仕様を生成してください。

## 利用可能なカラム
{columns}

## リクエスト
{message}

以下の形式で回答してください:
グラフを作成しました。

```chart_spec
{{"type": "bar|line|pie", "title": "グラフタイトル", "x": "X軸カラム", "y": "Y軸カラム"}}
```
"""
        response = self.model.generate_content(prompt)
        content = response.text

        # chart_specを抽出
        chart_spec = None
        spec_match = re.search(r"```chart_spec\s*(.*?)\s*```", content, re.DOTALL)
        if spec_match:
            try:
                chart_spec = json.loads(spec_match.group(1))
            except json.JSONDecodeError:
                pass

        return ChatResponse(type="chart", content=content, chart_spec=chart_spec)

    def _handle_analyze(self, message: str, context: dict[str, Any]) -> ChatResponse:
        """分析リクエストを処理"""
        df = context.get("df")
        data_info = self._get_data_info(df) if df is not None else ""

        prompt = f"""
以下のデータを分析してインサイトを提供してください。

## データ情報
{data_info}

## 分析リクエスト
{message}

分析結果を箇条書きで提供してください。
"""
        response = self.model.generate_content(prompt)
        return ChatResponse(type="insight", content=response.text)

    def _handle_summarize(self, message: str, context: dict[str, Any]) -> ChatResponse:
        """まとめリクエストを処理"""
        df = context.get("df")
        data_info = self._get_data_info(df) if df is not None else ""

        prompt = f"""
以下のデータをまとめてください。

## データ情報
{data_info}

## リクエスト
{message}

要点を簡潔にまとめてください。
"""
        response = self.model.generate_content(prompt)
        return ChatResponse(type="text", content=response.text)

    def _handle_general(self, message: str, context: dict[str, Any]) -> ChatResponse:
        """一般的な会話を処理"""
        prompt = f"""
あなたはデータ分析アシスタントです。以下のメッセージに応答してください。

メッセージ: {message}

フレンドリーに応答してください。データ分析について質問があれば案内してください。
"""
        response = self.model.generate_content(prompt)
        return ChatResponse(type="text", content=response.text)

    def _get_data_info(self, df: pd.DataFrame) -> str:
        """データ情報を文字列で取得"""
        if df is None:
            return "データがありません"

        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        stats = {}
        for col in numeric_cols:
            stats[col] = {
                "sum": float(df[col].sum()),
                "mean": float(df[col].mean()),
                "min": float(df[col].min()),
                "max": float(df[col].max()),
            }

        return f"""
行数: {len(df)}
カラム: {", ".join(df.columns.tolist())}
数値カラムの統計: {json.dumps(stats, ensure_ascii=False)}
"""

    def build_context(self, df: pd.DataFrame, chat_history: list[dict[str, str]]) -> dict[str, Any]:
        """
        AIに渡すコンテキストを構築する

        Args:
            df: データフレーム
            chat_history: 会話履歴

        Returns:
            dict: コンテキスト情報
        """
        return {
            "data_summary": f"行数: {len(df)}, カラム数: {len(df.columns)}",
            "columns": ", ".join(df.columns.tolist()),
            "chat_history": chat_history[-10:],  # 直近10件に制限
        }

    def generate_chart_spec(self, request: str, columns: list[str]) -> dict[str, Any]:
        """
        グラフ仕様を生成する

        Args:
            request: ユーザーリクエスト
            columns: 利用可能なカラム

        Returns:
            dict: グラフ仕様
        """
        prompt = f"""
以下のリクエストに基づいてグラフ仕様をJSON形式で生成してください。

利用可能なカラム: {columns}
リクエスト: {request}

JSON形式のみで回答してください:
{{"type": "bar|line|pie", "title": "タイトル", "x": "Xカラム", "y": "Yカラム", "aggregation": "sum|mean|count"}}
"""
        response = self.model.generate_content(prompt)
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            # デフォルト仕様を返す
            return {
                "type": "bar",
                "title": request,
                "x": columns[0],
                "y": columns[1] if len(columns) > 1 else columns[0],
            }

    def generate_chart_data(self, spec: dict[str, Any], df: pd.DataFrame) -> dict[str, Any]:
        """
        グラフ仕様に基づいてデータを集計する

        Args:
            spec: グラフ仕様
            df: データフレーム

        Returns:
            dict: 集計されたグラフデータ
        """
        x_col = spec.get("x")
        y_col = spec.get("y")
        aggregation = spec.get("aggregation", "sum")

        if x_col not in df.columns or y_col not in df.columns:
            return {"labels": [], "values": []}

        if aggregation == "sum":
            grouped = df.groupby(x_col)[y_col].sum()
        elif aggregation == "mean":
            grouped = df.groupby(x_col)[y_col].mean()
        elif aggregation == "count":
            grouped = df.groupby(x_col)[y_col].count()
        else:
            grouped = df.groupby(x_col)[y_col].sum()

        return {"labels": list(grouped.index), "values": list(grouped.values)}

    def generate_chart_html(self, spec: dict[str, Any], data: dict[str, Any]) -> str:
        """
        グラフHTMLを生成する

        Args:
            spec: グラフ仕様
            data: グラフデータ

        Returns:
            str: Chart.js を使ったHTML
        """
        chart_type = spec.get("type", "bar")
        title = spec.get("title", "Chart")
        labels = json.dumps(data.get("labels", []))
        values = json.dumps(data.get("values", []))

        return f"""
<div style="width: 100%; max-width: 600px;">
    <canvas id="additionalChart"></canvas>
    <script>
        new Chart(document.getElementById('additionalChart'), {{
            type: '{chart_type}',
            data: {{
                labels: {labels},
                datasets: [{{
                    label: '{title}',
                    data: {values},
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    title: {{
                        display: true,
                        text: '{title}'
                    }}
                }}
            }}
        }});
    </script>
</div>
"""
