"""
AIGenerator のテスト

責務:
- Blueprint（グラフ構成案）の生成
- Python集計コードの生成
- HTMLダッシュボードの生成
- ワンショット生成（統合）
"""

from unittest.mock import Mock

import pytest

from src.services.ai_generator import AIGenerator, GenerationResult


class TestAIGeneratorBlueprint:
    """Blueprint生成機能のテスト"""

    def test_generate_blueprint_returns_string(self, sample_dataframe):
        """Blueprintが文字列で返される"""
        mock_model = Mock()
        mock_model.generate_content.return_value = Mock(text="## Blueprint\n- Chart 1")

        generator = AIGenerator(model=mock_model)
        blueprint = generator.generate_blueprint(sample_dataframe)

        assert isinstance(blueprint, str)
        assert len(blueprint) > 0

    def test_generate_blueprint_calls_model_with_summary(self, sample_dataframe):
        """モデルにデータサマリーが渡される"""
        mock_model = Mock()
        mock_model.generate_content.return_value = Mock(text="Blueprint")

        generator = AIGenerator(model=mock_model)
        generator.generate_blueprint(sample_dataframe)

        # generate_contentが呼ばれたことを確認
        mock_model.generate_content.assert_called_once()
        call_args = mock_model.generate_content.call_args[0][0]

        # プロンプトにカラム情報が含まれている
        assert "売上" in call_args or "columns" in call_args.lower()


class TestAIGeneratorCodeGeneration:
    """コード生成機能のテスト"""

    def test_generate_code_returns_tuple(self, sample_dataframe):
        """Python, HTMLのタプルで返される"""
        mock_model = Mock()
        mock_model.generate_content.return_value = Mock(
            text="""
```python
def aggregate_all_data(df):
    return {"kpi": {}}
```

```html
<!DOCTYPE html><html></html>
```
"""
        )

        generator = AIGenerator(model=mock_model)
        py_code, html_code = generator.generate_code("Blueprint here")

        assert isinstance(py_code, str)
        assert isinstance(html_code, str)

    def test_generate_code_extracts_python_block(self, sample_dataframe):
        """Pythonコードブロックが抽出される"""
        mock_model = Mock()
        mock_model.generate_content.return_value = Mock(
            text="""
```python
def aggregate_all_data(df):
    result = {"kpi": {"total": 100}}
    return result
```

```html
<!DOCTYPE html><html></html>
```
"""
        )

        generator = AIGenerator(model=mock_model)
        py_code, _ = generator.generate_code("Blueprint")

        assert "def aggregate_all_data" in py_code
        assert "return result" in py_code

    def test_generate_code_extracts_html_block(self, sample_dataframe):
        """HTMLコードブロックが抽出される"""
        mock_model = Mock()
        mock_model.generate_content.return_value = Mock(
            text="""
```python
def aggregate_all_data(df):
    return {}
```

```html
<!DOCTYPE html>
<html>
<head><title>Dashboard</title></head>
<body></body>
</html>
```
"""
        )

        generator = AIGenerator(model=mock_model)
        _, html_code = generator.generate_code("Blueprint")

        assert "<!DOCTYPE html>" in html_code
        assert "<html>" in html_code

    def test_generate_code_raises_on_missing_python(self):
        """Pythonブロックがない場合はエラー"""
        mock_model = Mock()
        mock_model.generate_content.return_value = Mock(
            text="""
```html
<!DOCTYPE html><html></html>
```
"""
        )

        generator = AIGenerator(model=mock_model)

        with pytest.raises(ValueError, match="Python"):
            generator.generate_code("Blueprint")

    def test_generate_code_raises_on_missing_html(self):
        """HTMLブロックがない場合はエラー"""
        mock_model = Mock()
        mock_model.generate_content.return_value = Mock(
            text="""
```python
def aggregate_all_data(df):
    return {}
```
"""
        )

        generator = AIGenerator(model=mock_model)

        with pytest.raises(ValueError, match="HTML"):
            generator.generate_code("Blueprint")


class TestAIGeneratorExecution:
    """コード実行機能のテスト"""

    def test_execute_aggregation_returns_dict(self, sample_dataframe):
        """集計結果が辞書で返される"""
        py_code = """
def aggregate_all_data(df):
    return {"kpi": {"total_sales": int(df['売上'].sum())}}
"""
        generator = AIGenerator(model=Mock())
        result = generator.execute_aggregation(py_code, sample_dataframe)

        assert isinstance(result, dict)
        assert "kpi" in result

    def test_execute_aggregation_correct_values(self, sample_dataframe):
        """集計値が正しい"""
        py_code = """
def aggregate_all_data(df):
    return {
        "kpi": {
            "total_sales": int(df['売上'].sum()),
            "count": len(df)
        }
    }
"""
        generator = AIGenerator(model=Mock())
        result = generator.execute_aggregation(py_code, sample_dataframe)

        assert result["kpi"]["total_sales"] == 65000
        assert result["kpi"]["count"] == 5

    def test_execute_aggregation_raises_on_syntax_error(self, sample_dataframe):
        """構文エラーの場合は例外"""
        py_code = """
def aggregate_all_data(df)  # missing colon
    return {}
"""
        generator = AIGenerator(model=Mock())

        with pytest.raises(Exception):
            generator.execute_aggregation(py_code, sample_dataframe)

    def test_execute_aggregation_raises_on_missing_function(self, sample_dataframe):
        """aggregate_all_data関数がない場合は例外"""
        py_code = """
def some_other_function(df):
    return {}
"""
        generator = AIGenerator(model=Mock())

        with pytest.raises(ValueError, match="aggregate_all_data"):
            generator.execute_aggregation(py_code, sample_dataframe)


class TestAIGeneratorAssembly:
    """HTML組み立て機能のテスト"""

    def test_assemble_html_injects_json(self):
        """JSONデータがHTMLに注入される"""
        html_template = """
<!DOCTYPE html>
<html>
<script>const dashboardData = {{JSON_DATA}};</script>
</html>
"""
        data = {"kpi": {"total": 100}}

        generator = AIGenerator(model=Mock())
        result = generator.assemble_html(html_template, data)

        assert "{{JSON_DATA}}" not in result
        assert '"kpi"' in result
        assert '"total": 100' in result

    def test_assemble_html_adds_direct_view_script(self):
        """Direct View用のスクリプトが追加される"""
        html_template = """
<!DOCTYPE html>
<html>
<body></body>
</html>
"""
        data = {"kpi": {}}

        generator = AIGenerator(model=Mock())
        result = generator.assemble_html(html_template, data)

        assert "Direct View" in result or "renderCharts" in result


class TestAIGeneratorOneshot:
    """ワンショット生成機能のテスト"""

    def test_generate_oneshot_returns_generation_result(self, sample_dataframe):
        """GenerationResultオブジェクトが返される"""
        mock_model = Mock()

        # Blueprint生成
        mock_model.generate_content.side_effect = [
            Mock(text="## Blueprint\n| No | Chart |"),
            Mock(
                text="""
```python
def aggregate_all_data(df):
    return {"kpi": {"total": int(df['売上'].sum())}, "charts": {}}
```

```html
<!DOCTYPE html>
<html>
<script>const dashboardData = {{JSON_DATA}};</script>
<body></body>
</html>
```
"""
            ),
        ]

        generator = AIGenerator(model=mock_model)
        result = generator.generate_oneshot(sample_dataframe)

        assert isinstance(result, GenerationResult)

    def test_generate_oneshot_contains_html(self, sample_dataframe):
        """結果にHTMLが含まれる"""
        mock_model = Mock()
        mock_model.generate_content.side_effect = [
            Mock(text="Blueprint"),
            Mock(
                text="""
```python
def aggregate_all_data(df):
    return {"kpi": {}, "charts": {}}
```

```html
<!DOCTYPE html><html><body></body></html>
```
"""
            ),
        ]

        generator = AIGenerator(model=mock_model)
        result = generator.generate_oneshot(sample_dataframe)

        assert result.html is not None
        assert "<!DOCTYPE html>" in result.html

    def test_generate_oneshot_contains_data(self, sample_dataframe):
        """結果に集計データが含まれる"""
        mock_model = Mock()
        mock_model.generate_content.side_effect = [
            Mock(text="Blueprint"),
            Mock(
                text="""
```python
def aggregate_all_data(df):
    return {"kpi": {"total": 65000}, "charts": {}}
```

```html
<!DOCTYPE html><html><script>const dashboardData = {{JSON_DATA}};</script><body></body></html>
```
"""
            ),
        ]

        generator = AIGenerator(model=mock_model)
        result = generator.generate_oneshot(sample_dataframe)

        assert result.data is not None
        assert result.data["kpi"]["total"] == 65000

    def test_generate_oneshot_calls_progress_callback(self, sample_dataframe):
        """進捗コールバックが呼ばれる"""
        mock_model = Mock()
        mock_model.generate_content.side_effect = [
            Mock(text="Blueprint"),
            Mock(
                text="""
```python
def aggregate_all_data(df):
    return {"kpi": {}, "charts": {}}
```

```html
<!DOCTYPE html><html><body></body></html>
```
"""
            ),
        ]

        progress_calls = []

        def progress_callback(step, message):
            progress_calls.append((step, message))

        generator = AIGenerator(model=mock_model)
        generator.generate_oneshot(sample_dataframe, progress_callback=progress_callback)

        assert len(progress_calls) >= 3  # 少なくとも3ステップ
        steps = [call[0] for call in progress_calls]
        assert 1 in steps
        assert 2 in steps
