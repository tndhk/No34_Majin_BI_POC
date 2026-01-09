import pandas as pd
import pytest
import ast
from unittest.mock import Mock, patch
from src.services.ai_generator import (
    AIGenerator,
    _prepare_series_categories,
    _prepare_df_categories,
    _SafeMethodTransformer,
    _rewrite_generated_calls,
)

class TestAIGeneratorCoverageGap:
    """CIカバレッジ向上のための追加テスト"""

    def test_prepare_series_categories_existing(self):
        # Given: Series with existing category
        # Perspective: AIG-N-01 (Equivalence - Normal)
        s = pd.Series(["a", "b"], dtype="category")
        
        # When: Preparing with existing value
        res = _prepare_series_categories(s, "a")
        
        # Then: Returns same
        assert len(res.cat.categories) == 2

    def test_prepare_series_categories_new(self):
        # Given: Series and a new value
        # Perspective: AIG-N-02 (Equivalence - Normal)
        s = pd.Series(["a", "b"], dtype="category")
        
        # When: Preparing with new value
        res = _prepare_series_categories(s, "c")
        
        # Then: Category added
        assert "c" in res.cat.categories

    def test_prepare_df_categories_no_cat_cols(self):
        # Given: DF without categorical columns
        # Perspective: AIG-N-03 (Boundary - Empty)
        df = pd.DataFrame({"A": [1, 2]})
        
        # When: Preparing
        res = _prepare_df_categories(df, "val")
        
        # Then: Returns same
        assert res is df

    def test_prepare_df_categories_dict_missing_col(self):
        # Given: DF with category and dict value missing that col
        # Perspective: AIG-N-04 (Equivalence - Normal)
        df = pd.DataFrame({"A": pd.Series(["a"], dtype="category")})
        
        # When: Preparing with dict lacking "A"
        res = _prepare_df_categories(df, {"B": "val"})
        
        # Then: No change
        assert "val" not in res["A"].cat.categories

    def test_safe_method_transformer_tolist_with_args(self):
        # Given: tolist call with args (which shouldn't happen usually but for coverage)
        # Perspective: AIG-N-05 (Equivalence - Normal)
        code = "df.tolist(True)"
        tree = ast.parse(code)
        
        # When: Transforming
        transformer = _SafeMethodTransformer()
        new_tree = transformer.visit(tree)
        
        # Then: Not transformed to _safe_tolist
        unparsed = ast.unparse(new_tree)
        assert "_safe_tolist" not in unparsed

    def test_safe_method_transformer_mul(self):
        # Given: mul call
        # Perspective: AIG-N-06 (Equivalence - Normal)
        code = "obj.mul(3)"
        tree = ast.parse(code)
        
        # When: Transforming
        transformer = _SafeMethodTransformer()
        new_tree = transformer.visit(tree)
        
        # Then: Transformed to _safe_mul
        unparsed = ast.unparse(new_tree)
        assert "_safe_mul" in unparsed

    def test_repair_python_syntax_error_success(self, sample_dataframe):
        # Given: Generator with model that returns repaired code
        # Perspective: AIG-A-01 (Abnormal - Recovery)
        mock_model = Mock()
        mock_model.generate_content.return_value = Mock(text="```python\ndef aggregate_all_data(df):\n    return {'kpi': 'fixed'}\n```")
        generator = AIGenerator(model=mock_model)
        
        # When: Executing code with syntax error
        bad_code = "def aggregate_all_data(df) # Error"
        result = generator.execute_aggregation(bad_code, sample_dataframe)
        
        # Then: AI repair logic triggered and succeeded
        assert result['kpi'] == 'fixed'
        assert mock_model.generate_content.called

    def test_repair_python_runtime_error_success(self, sample_dataframe):
        # Given: Code that raises KeyError
        # Perspective: AIG-A-02 (Abnormal - Recovery)
        mock_model = Mock()
        mock_model.generate_content.return_value = Mock(text="```python\ndef aggregate_all_data(df):\n    return {'kpi': 'recovered'}\n```")
        generator = AIGenerator(model=mock_model)
        
        bad_code = "def aggregate_all_data(df):\n    raise KeyError('missing')"
        
        # When: Executing
        result = generator.execute_aggregation(bad_code, sample_dataframe)
        
        # Then: Succeeded after repair
        assert result['kpi'] == 'recovered'

    def test_assemble_html_no_body_tag(self):
        # Given: HTML without </body>
        # Perspective: AIG-B-01 (Boundary - Abnormal)
        html = "<html>No body</html>"
        generator = AIGenerator(model=Mock())
        
        # When: Assembling
        result = generator.assemble_html(html, {"kpi": {}})
        
        # Then: Script appended to the end
        assert "const dashboardData =" in result
        assert "Direct View" in result

    def test_coerce_json_value_edge_cases(self):
        # Given: Objects with .item() or .tolist() that might or might not fail
        # Perspective: Coverage for lines 233-242
        class HasItem:
            def item(self): return 42
        class HasItemFail:
            def item(self): raise ValueError("failed")
        class HasToList:
            def tolist(self): return [1, 2, 3]
        class HasToListFail:
            def tolist(self): raise ValueError("failed")
        
        # When & Then:
        from src.services.ai_generator import _coerce_json_value
        assert _coerce_json_value(HasItem()) == 42
        assert isinstance(_coerce_json_value(HasItemFail()), HasItemFail)
        assert _coerce_json_value(HasToList()) == [1, 2, 3]
        assert isinstance(_coerce_json_value(HasToListFail()), HasToListFail)
        assert _coerce_json_value(None) is None

    def test_repair_python_syntax_error_double_failure(self, sample_dataframe):
        # Given: Repaired code also has syntax error
        # Perspective: Abnormal - Nested Failure
        mock_model = Mock()
        # First call returns bad code, second call returns also bad code
        mock_model.generate_content.side_effect = [
            Mock(text="```python\ndef aggregate_all_data(df) # typo again\n```"),
            Mock(text="irrelevent")
        ]
        generator = AIGenerator(model=mock_model)
        
        # When & Then: Raises ValueError eventually
        with pytest.raises(ValueError, match="修正後の集計コードに構文エラーがあります"):
            generator.execute_aggregation("def foo()", sample_dataframe)

    def test_repair_python_runtime_error_double_failure(self, sample_dataframe):
        # Given: Repaired code also has runtime error
        # Perspective: Abnormal - Nested Failure
        mock_model = Mock()
        # Returns code that still raises an error
        mock_model.generate_content.return_value = Mock(text="```python\ndef aggregate_all_data(df):\n    raise RuntimeError('still failing')\n```")
        generator = AIGenerator(model=mock_model)
        
        # When & Then: Raises ValueError eventually
        with pytest.raises(ValueError, match="修正後の集計コードの実行に失敗しました"):
            generator.execute_aggregation("def aggregate_all_data(df): raise ValueError()", sample_dataframe)
