import pytest
import pandas as pd
from io import StringIO, BytesIO


@pytest.fixture
def sample_csv_utf8():
    """UTF-8エンコードのサンプルCSVデータ"""
    return """日付,商品名,売上,地域
2024-01-01,商品A,10000,東京
2024-01-02,商品B,15000,大阪
2024-01-03,商品A,12000,東京
2024-01-04,商品C,8000,福岡
2024-01-05,商品B,20000,大阪"""


@pytest.fixture
def sample_csv_shiftjis(sample_csv_utf8):
    """Shift_JISエンコードのサンプルCSVデータ（バイト列）"""
    return sample_csv_utf8.encode('shift_jis')


@pytest.fixture
def sample_dataframe():
    """サンプルDataFrame"""
    return pd.DataFrame({
        '日付': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05'],
        '商品名': ['商品A', '商品B', '商品A', '商品C', '商品B'],
        '売上': [10000, 15000, 12000, 8000, 20000],
        '地域': ['東京', '大阪', '東京', '福岡', '大阪']
    })


@pytest.fixture
def large_dataframe():
    """大規模データ用DataFrame（1000行）"""
    import random
    random.seed(42)

    dates = pd.date_range('2024-01-01', periods=1000, freq='D')
    products = ['商品A', '商品B', '商品C', '商品D', '商品E']
    regions = ['東京', '大阪', '福岡', '名古屋', '札幌']

    return pd.DataFrame({
        '日付': dates,
        '商品名': [random.choice(products) for _ in range(1000)],
        '売上': [random.randint(5000, 50000) for _ in range(1000)],
        '地域': [random.choice(regions) for _ in range(1000)]
    })
