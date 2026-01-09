"""
AIGenerator - AI を使ったダッシュボード生成

責務:
- Blueprint（グラフ構成案）の生成
- Python集計コードの生成
- HTMLダッシュボードの生成
- ワンショット生成（統合）
"""

import json
import re
from collections.abc import Callable
from dataclasses import dataclass
from io import StringIO
from typing import Any

import pandas as pd

from prompts import PHASE2_PROMPT_TEMPLATE


@dataclass
class GenerationResult:
    """ダッシュボード生成結果"""

    html: str
    data: dict[str, Any]
    blueprint: str


class AIGenerator:
    """AIを使ったダッシュボード生成を行うクラス"""

    def __init__(self, model):
        """
        Args:
            model: Gemini モデルインスタンス
        """
        self.model = model

    def generate_blueprint(self, df: pd.DataFrame) -> str:
        """
        データフレームからBlueprintを生成する

        Args:
            df: 対象のDataFrame

        Returns:
            str: Blueprint（グラフ構成案）のMarkdown
        """
        # データサマリーを作成
        columns_str = ", ".join(df.columns.tolist())
        buffer = StringIO()
        df.head(5).to_csv(buffer, index=False)
        sample_data = buffer.getvalue()

        prompt = f"""
以下のデータ構造を持つCSVファイルを分析し、20個以上のグラフ構成案を提案してください。

## データ要約
- カラム名: {columns_str}
- データサンプル (5行):
{sample_data}

## 出力フォーマット
Markdown形式で出力してください。
"""
        response = self.model.generate_content(prompt)
        return response.text

    def generate_code(self, blueprint: str) -> tuple[str, str]:
        """
        Blueprintからコードを生成する

        Args:
            blueprint: 承認されたBlueprint

        Returns:
            Tuple[str, str]: (Python集計コード, HTMLダッシュボード)

        Raises:
            ValueError: コードブロックが見つからない場合
        """
        prompt = PHASE2_PROMPT_TEMPLATE.replace("{{BLUEPRINT}}", blueprint)
        response = self.model.generate_content(prompt)
        content = response.text

        # Pythonコードを抽出（柔軟なパターン）
        py_match = re.search(r"`{3,}\s*python\s*\n(.*?)\n`{3,}", content, re.DOTALL | re.IGNORECASE)
        if not py_match:
            raise ValueError("Pythonコードブロックが見つかりません")
        py_code = py_match.group(1).strip()

        # HTMLコードを抽出（柔軟なパターン）
        html_match = re.search(r"`{3,}\s*html?\s*\n(.*?)\n`{3,}", content, re.DOTALL | re.IGNORECASE)

        # フォールバック: HTMLタグで直接検索
        if not html_match:
            html_match = re.search(r"(<!DOCTYPE html>.*?</html>)", content, re.DOTALL | re.IGNORECASE)

        if not html_match:
            raise ValueError("HTMLコードブロックが見つかりません")
        html_code = html_match.group(1).strip()

        return py_code, html_code

    def execute_aggregation(self, py_code: str, df: pd.DataFrame) -> dict[str, Any]:
        """
        Python集計コードを実行する

        Args:
            py_code: 集計コード
            df: 対象のDataFrame

        Returns:
            dict: 集計結果

        Raises:
            ValueError: aggregate_all_data関数が定義されていない場合
            Exception: 実行時エラー
        """
        # コードを実行
        scope = {"pd": pd, "df": df}
        exec(py_code, scope, scope)

        if "aggregate_all_data" not in scope:
            raise ValueError("aggregate_all_data 関数が定義されていません")

        return scope["aggregate_all_data"](df)

    def assemble_html(self, html_template: str, data: dict[str, Any]) -> str:
        """
        HTMLテンプレートにデータを注入する

        Args:
            html_template: HTMLテンプレート
            data: 注入するデータ

        Returns:
            str: 完成したHTML
        """
        # JSONデータを注入
        json_data = json.dumps(data, ensure_ascii=False)
        html = html_template.replace("{{JSON_DATA}}", json_data)

        # Direct View用スクリプトを追加
        direct_view_script = """
<script>
    // Direct View: Auto-initialize dashboard
    const originalOnLoad = window.onload;
    window.onload = function() {
        if (originalOnLoad) originalOnLoad();
        console.log("Direct View: Dashboard initialized");
        if (typeof renderCharts === 'function') renderCharts();
    };
</script>
"""
        html = html.replace("</body>", f"{direct_view_script}</body>")

        return html

    def generate_oneshot(
        self, df: pd.DataFrame, progress_callback: Callable[[int, str], None] | None = None
    ) -> GenerationResult:
        """
        ワンショットでダッシュボードを生成する

        Args:
            df: 対象のDataFrame
            progress_callback: 進捗通知コールバック (step, message)

        Returns:
            GenerationResult: 生成結果
        """

        def notify(step: int, message: str):
            if progress_callback:
                progress_callback(step, message)

        # Step 1: Blueprint生成
        notify(1, "データ構造を分析中...")
        blueprint = self.generate_blueprint(df)

        # Step 2: コード生成
        notify(2, "ダッシュボードを設計中...")
        py_code, html_template = self.generate_code(blueprint)

        # Step 3: 集計実行
        notify(3, "データを集計中...")
        aggregated_data = self.execute_aggregation(py_code, df)

        # Step 4: HTML組み立て
        notify(4, "ダッシュボードを構築中...")
        final_html = self.assemble_html(html_template, aggregated_data)

        return GenerationResult(html=final_html, data=aggregated_data, blueprint=blueprint)
