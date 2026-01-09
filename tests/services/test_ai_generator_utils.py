import pandas as pd
import pytest
from src.services.ai_generator import (
    _safe_tolist,
    _safe_mul,
    _safe_fillna,
    _coerce_json_value,
    _format_syntax_error,
    _format_runtime_error,
)

def test_safe_tolist():
    # Given: Various inputs
    s = pd.Series([1, 2, 3])
    l = [1, 2, 3]
    t = (1, 2, 3)
    val = 1
    
    # When & Then:
    assert _safe_tolist(s) == [1, 2, 3]
    assert _safe_tolist(l) == [1, 2, 3]
    assert _safe_tolist(t) == [1, 2, 3]
    assert _safe_tolist(val) == [1]

def test_safe_mul():
    # Given: Various inputs
    s = pd.Series([2, 2, 2])
    val = 2
    
    # When & Then:
    pd.testing.assert_series_equal(_safe_mul(s, 3), pd.Series([6, 6, 6]))
    assert _safe_mul(val, 3) == 6
    with pytest.raises(TypeError):
        _safe_mul(val)

def test_safe_fillna():
    # Given: DF and Series with categories
    df = pd.DataFrame({"A": pd.Series(["a", "b", None], dtype="category")})
    s = pd.Series(["a", "b", None], dtype="category")
    
    # When:
    res_df = _safe_fillna(df, "unknown")
    res_s = _safe_fillna(s, "unknown")
    
    # Then:
    assert res_df["A"][2] == "unknown"
    assert res_s[2] == "unknown"
    assert _safe_fillna(1, 0) == 1

def test_coerce_json_value():
    # Given: Mixed object types including Pandas types
    data = {
        "series": pd.Series([1, 2]),
        "timestamp": pd.Timestamp("2024-01-01"),
        "timedelta": pd.Timedelta(seconds=60),
        "na": pd.NA,
        "list": [1, 2],
        "dict": {"a": 1},
        "bytes": b"hello"
    }
    
    # When:
    coerced = _coerce_json_value(data)
    
    # Then:
    assert coerced["series"] == [1, 2]
    assert coerced["timestamp"] == "2024-01-01T00:00:00"
    assert coerced["timedelta"] == 60.0
    assert coerced["na"] is None
    assert coerced["bytes"] == "hello"

def test_format_syntax_error():
    # Given: A simulated SyntaxError
    code = "def foo()\n  pass"
    err = SyntaxError("invalid syntax", ("test.py", 1, 10, code))
    
    # When:
    formatted = _format_syntax_error(err, code)
    
    # Then:
    assert "invalid syntax" in formatted
    assert "line 1" in formatted
    assert "^" in formatted

def test_format_runtime_error():
    # Given: An exception
    err = ValueError("Something went wrong")
    
    # When:
    formatted = _format_runtime_error(err)
    
    # Then:
    assert formatted == "ValueError: Something went wrong"
