"""
AIGenerator - AI を使ったダッシュボード生成

責務:
- Blueprint（グラフ構成案）の生成
- Python集計コードの生成
- HTMLダッシュボードの生成
- ワンショット生成（統合）
"""

import ast
import json
import re
import traceback
from collections.abc import Callable
from dataclasses import dataclass
from io import StringIO
from typing import Any

import pandas as pd

from prompts import PHASE1_PROMPT_TEMPLATE, PHASE2_PROMPT_TEMPLATE

CHART_SAFETY_NET_SCRIPT = """
<script src="https://unpkg.com/lucide@latest"></script>
<script>
(function() {
    // === Chart.js Safety Net (Injected by AIGenerator) ===
    try {
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }

        if (typeof Chart !== 'undefined') {
            Chart.defaults.color = '#cbd5e1';
            Chart.defaults.borderColor = '#334155';
            Chart.defaults.font.family = "'DM Sans', sans-serif";
        }

        if (!window.ORACLE_COLORS) {
            window.ORACLE_COLORS = [
                '#38bdf8', '#fbbf24', '#818cf8', '#34d399', '#f472b6',
                '#2dd4bf', '#a78bfa', '#fb923c', '#9ca3af', '#60a5fa'
            ];
        }

        if (!window.assignOracleColors) {
            window.assignOracleColors = function(chartData, index) {
                var colors = window.ORACLE_COLORS;
                var color = colors[index % colors.length];
                if (!chartData || !chartData.datasets) return chartData;
                chartData.datasets.forEach(function(ds) {
                    if (ds.type === 'pie' || ds.type === 'doughnut') {
                        ds.backgroundColor = ds.backgroundColor || colors;
                        ds.borderColor = ds.borderColor || '#1e293b';
                    } else {
                        ds.backgroundColor = ds.backgroundColor || color;
                        ds.borderColor = ds.borderColor || color;
                    }
                });
                return chartData;
            };
        }
    } catch (e) {
        console.error('Chart.js Safety Net Error:', e);
    }
})();
</script>
"""

DIRECT_VIEW_SCRIPT = """
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


def _safe_tolist(obj: Any) -> list[Any]:
    if hasattr(obj, "tolist"):
        return obj.tolist()
    if isinstance(obj, list):
        return obj
    try:
        return list(obj)
    except TypeError:
        return [obj]


def _safe_mul(obj: Any, *args: Any, **kwargs: Any) -> Any:
    if hasattr(obj, "mul"):
        return obj.mul(*args, **kwargs)
    if not args:
        raise TypeError("mul requires an operand when used on scalars")
    return obj * args[0]


def _safe_fillna(obj: Any, *args: Any, **kwargs: Any) -> Any:
    if isinstance(obj, pd.DataFrame):
        value = args[0] if args else kwargs.get("value")
        if value is not None:
            obj = _prepare_df_categories(obj, value)
        return obj.fillna(*args, **kwargs)
    if isinstance(obj, pd.Series) and pd.api.types.is_categorical_dtype(obj):
        value = args[0] if args else kwargs.get("value")
        if value is not None:
            obj = _prepare_series_categories(obj, value)
        return obj.fillna(*args, **kwargs)
    if hasattr(obj, "fillna"):
        return obj.fillna(*args, **kwargs)
    return obj


def _prepare_series_categories(series: pd.Series, value: Any) -> pd.Series:
    if isinstance(value, dict):
        return series
    try:
        if value not in series.cat.categories:
            return series.cat.add_categories([value])
    except Exception:
        return series
    return series


def _prepare_df_categories(df: pd.DataFrame, value: Any) -> pd.DataFrame:
    cat_cols = df.select_dtypes(include=["category"]).columns
    if not len(cat_cols):
        return df
    df = df.copy()
    if isinstance(value, dict):
        for col in cat_cols:
            if col not in value:
                continue
            df[col] = _prepare_series_categories(df[col], value[col])
        return df
    for col in cat_cols:
        df[col] = _prepare_series_categories(df[col], value)
    return df


class _SafeMethodTransformer(ast.NodeTransformer):
    def visit_Call(self, node: ast.Call) -> ast.AST:
        self.generic_visit(node)
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == "tolist" and not node.args and not node.keywords:
                return ast.Call(
                    func=ast.Name(id="_safe_tolist", ctx=ast.Load()),
                    args=[node.func.value],
                    keywords=[],
                )
            if node.func.attr == "mul":
                return ast.Call(
                    func=ast.Name(id="_safe_mul", ctx=ast.Load()),
                    args=[node.func.value, *node.args],
                    keywords=node.keywords,
                )
            if node.func.attr == "fillna":
                return ast.Call(
                    func=ast.Name(id="_safe_fillna", ctx=ast.Load()),
                    args=[node.func.value, *node.args],
                    keywords=node.keywords,
                )
        return node


def _rewrite_generated_calls(py_code: str) -> str:
    try:
        tree = ast.parse(py_code)
    except SyntaxError:
        return py_code
    tree = _SafeMethodTransformer().visit(tree)
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)


def _extract_python_code(content: str) -> str | None:
    match = re.search(
        r"`{3,}\s*python\s*\n(.*?)\n`{3,}",
        content,
        re.DOTALL | re.IGNORECASE,
    )
    if not match:
        return None
    return match.group(1).strip()


def _format_syntax_error(error: SyntaxError, code: str) -> str:
    line_no = error.lineno or 0
    line_text = error.text or ""
    if not line_text and line_no:
        lines = code.splitlines()
        if 1 <= line_no <= len(lines):
            line_text = lines[line_no - 1]
    if not line_no or not line_text:
        return error.msg
    line_text = line_text.rstrip("\n")
    caret = ""
    if error.offset:
        caret = " " * (error.offset - 1) + "^"
    return f"{error.msg} (line {line_no})\n{line_text}\n{caret}".rstrip()


def _format_runtime_error(error: Exception) -> str:
    return f"{error.__class__.__name__}: {error}"


def _coerce_json_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _coerce_json_value(val) for key, val in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_coerce_json_value(item) for item in value]
    if isinstance(value, (bytes, bytearray)):
        return value.decode("utf-8", errors="replace")
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except Exception:
        pass
    if isinstance(value, (pd.Series, pd.Index)):
        return [_coerce_json_value(item) for item in value.tolist()]
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, pd.Timedelta):
        return value.total_seconds()
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    if hasattr(value, "tolist"):
        try:
            return value.tolist()
        except Exception:
            pass
    return value


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

        prompt = PHASE1_PROMPT_TEMPLATE.format(columns=columns_str, sample_data=sample_data)
        response = self.model.generate_content(prompt)
        return response.text

    def generate_code(self, blueprint: str, df: pd.DataFrame) -> tuple[str, str]:
        """
        Blueprintからコードを生成する

        Args:
            blueprint: 承認されたBlueprint
            df: データフレーム（カラム名参照用）

        Returns:
            Tuple[str, str]: (Python集計コード, HTMLダッシュボード)

        Raises:
            ValueError: コードブロックが見つからない場合
        """
        # カラムリストを文字列化 (Ground Truth)
        columns_str = ", ".join(df.columns.tolist())

        prompt = PHASE2_PROMPT_TEMPLATE.replace("{{BLUEPRINT}}", blueprint).replace(
            "{{COLUMNS}}", columns_str
        )
        response = self.model.generate_content(prompt)
        content = response.text

        # Pythonコードを抽出（柔軟なパターン）
        py_code = _extract_python_code(content)
        if not py_code:
            raise ValueError("Pythonコードブロックが見つかりません")

        # HTMLコードを抽出（柔軟なパターン）
        html_match = re.search(
            r"`{3,}\s*html?\s*\n(.*?)\n`{3,}", content, re.DOTALL | re.IGNORECASE
        )

        # フォールバック: HTMLタグで直接検索
        if not html_match:
            html_match = re.search(
                r"(<!DOCTYPE html>.*?</html>)", content, re.DOTALL | re.IGNORECASE
            )

        if not html_match:
            raise ValueError("HTMLコードブロックが見つかりません")
        html_code = html_match.group(1).strip()

        return py_code, html_code

    def _repair_python_code(self, py_code: str, error: SyntaxError) -> str | None:
        generate_content = getattr(self.model, "generate_content", None)
        if not callable(generate_content):
            return None
        error_line = (error.text or "").rstrip()
        location = f"line {error.lineno or 0}"
        if error.offset:
            location = f"{location}, column {error.offset}"
        prompt = (
            "The following Python code has a syntax error. Fix it and return only "
            "valid Python code.\n"
            "Keep the function name aggregate_all_data and preserve the output "
            "schema expected by the HTML.\n"
            f"Error: {error.msg} ({location})\n"
            f"Error line: {error_line}\n\n"
            "Python code:\n"
            f"{py_code}\n"
        )
        response = generate_content(prompt)
        content = getattr(response, "text", None)
        if not isinstance(content, str):
            return None
        content = content.strip()
        if not content:
            return None
        extracted = _extract_python_code(content)
        return extracted or content

    def _repair_runtime_error(self, py_code: str, error: Exception, df: pd.DataFrame) -> str | None:
        generate_content = getattr(self.model, "generate_content", None)
        if not callable(generate_content):
            return None
        columns = ", ".join([str(col) for col in df.columns.tolist()])
        error_details = _format_runtime_error(error)
        trace = traceback.format_exc()
        prompt = (
            "The following Python code raised a runtime error when calling "
            "aggregate_all_data(df). Fix it and return only valid Python code.\n"
            "Keep the function name aggregate_all_data and preserve the output "
            "schema expected by the HTML.\n"
            f"Error: {error_details}\n"
            f"DataFrame columns: {columns}\n"
            f"Traceback:\n{trace}\n\n"
            "Python code:\n"
            f"{py_code}\n"
        )
        response = generate_content(prompt)
        content = getattr(response, "text", None)
        if not isinstance(content, str):
            return None
        content = content.strip()
        if not content:
            return None
        extracted = _extract_python_code(content)
        return extracted or content

    def _create_scope(self, df: pd.DataFrame) -> dict[str, Any]:
        return {
            "pd": pd,
            "df": df,
            "_safe_tolist": _safe_tolist,
            "_safe_mul": _safe_mul,
            "_safe_fillna": _safe_fillna,
        }

    def _exec_code_safe(self, code: str, original_code: str, scope: dict[str, Any]) -> None:
        try:
            exec(code, scope, scope)
        except SyntaxError as e:
            repaired = self._repair_python_code(original_code, e)
            if not repaired:
                msg = _format_syntax_error(e, code)
                raise ValueError(f"生成された集計コードに構文エラーがあります: {msg}") from e

            repaired_code = _rewrite_generated_calls(repaired)
            try:
                exec(repaired_code, scope, scope)
            except SyntaxError as re:
                msg = _format_syntax_error(re, repaired_code)
                raise ValueError(f"修正後の集計コードに構文エラーがあります: {msg}") from re

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
        normalized_code = _rewrite_generated_calls(py_code)
        scope = self._create_scope(df)

        self._exec_code_safe(normalized_code, py_code, scope)

        if "aggregate_all_data" not in scope:
            raise ValueError("aggregate_all_data 関数が定義されていません")

        try:
            return scope["aggregate_all_data"](df)
        except Exception as error:
            repaired = self._repair_runtime_error(py_code, error, df)
            if not repaired:
                raise ValueError(
                    f"集計コードの実行に失敗しました: {_format_runtime_error(error)}"
                ) from error

            # Repaired code execution
            normalized_repaired = _rewrite_generated_calls(repaired)
            scope = self._create_scope(df)
            self._exec_code_safe(normalized_repaired, repaired, scope)

            if "aggregate_all_data" not in scope:
                raise ValueError("修正後のaggregate_all_data 関数が定義されていません") from error

            try:
                return scope["aggregate_all_data"](df)
            except Exception as repaired_error:
                raise ValueError(
                    "修正後の集計コードの実行に失敗しました: "
                    f"{_format_runtime_error(repaired_error)}"
                ) from repaired_error

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
        safe_data = _coerce_json_value(data)
        json_data = json.dumps(safe_data, ensure_ascii=False)

        # 1. プレースホルダーの置換（空白許容）
        # {{JSON_DATA}}, {{ JSON_DATA }}, {JSON_DATA} 等に対応
        pattern = r"\{\{\s*JSON_DATA\s*\}\}"

        if re.search(pattern, html_template):
            html = re.sub(pattern, lambda _: json_data, html_template)
        else:
            # 2. フォールバック: プレースホルダーがない場合
            # const dashboardData = ... ; を探して置換
            # DOTALLを使って複数行に対応
            var_pattern = r"(const\s+dashboardData\s*=\s*)(.*?)(\s*;)"

            # 既存の dashboardData があるか確認（複数行対応）
            match = re.search(var_pattern, html_template, re.DOTALL)

            if match:
                # JSONデータが安全に置換されるようにエスケープ処理などは json.dumps で済んでいる
                # 後方参照を使って variable 定義を書き換え
                html = re.sub(
                    var_pattern, f"\\1{json_data}\\3", html_template, count=1, flags=re.DOTALL
                )
            else:
                # 3. 最終手段: scriptタグを強制挿入
                # 既存の dashboardData が中途半端に存在して重複エラーになるのを防ぐため、念のため単純な置換も試みる
                if "const dashboardData =" in html_template:
                    # Regexで拾えなかったが文字列としては存在する場合、コメントアウトするなどして無効化したいが、
                    # ここでは単純に追記モード（リスクあり）ではなく、警告をログに残すべきだが、
                    # 実用上は injection_script を body 末尾に追加することで overwrite はできない（const再宣言エラーになる）。
                    # なので、var_pattern を緩和して再トライ
                    loose_pattern = r"const\s+dashboardData\s*="
                    html = re.sub(
                        loose_pattern,
                        f"// replaced\nconst dashboardData = {json_data}; //",
                        html_template,
                        count=1,
                    )
                else:
                    # bodyの閉じタグの直前に挿入
                    injection_script = f"<script>const dashboardData = {json_data};</script>"
                    if "</body>" in html_template:
                        html = html_template.replace("</body>", f"{injection_script}</body>")
                    else:
                        html = html_template + injection_script

        # Helper for safer injection
        def inject_script(target_html, script):
            if "</body>" in target_html:
                return target_html.replace("</body>", f"{script}</body>")
            return target_html + script

        # Chart.js Safety Net: 常にカラー関数とデフォルト設定を注入
        html = inject_script(html, CHART_SAFETY_NET_SCRIPT)

        # Direct View用スクリプトを追加
        html = inject_script(html, DIRECT_VIEW_SCRIPT)

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
        py_code, html_template = self.generate_code(blueprint, df)

        # Step 3: 集計実行
        notify(3, "データを集計中...")
        aggregated_data = self.execute_aggregation(py_code, df)

        # Step 4: HTML組み立て
        notify(4, "ダッシュボードを構築中...")
        final_html = self.assemble_html(html_template, aggregated_data)

        return GenerationResult(html=final_html, data=aggregated_data, blueprint=blueprint)
