"""
大規模データ性能テスト

目的:
- 大規模データでの処理時間を計測
- メモリ使用量の確認
- ボトルネックの特定
"""

import time
from io import StringIO
from unittest.mock import Mock

import numpy as np
import pandas as pd
import pytest

from src.services.ai_generator import AIGenerator
from src.services.chat_handler import ChatHandler
from src.services.data_processor import DataProcessor


def generate_large_dataframe(rows: int) -> pd.DataFrame:
    """大規模テストデータを生成"""
    np.random.seed(42)

    regions = ["東京", "大阪", "名古屋", "福岡", "札幌", "仙台", "広島", "神戸"]
    products = [f"商品{i}" for i in range(1, 51)]  # 50商品
    categories = ["食品", "衣料", "電化製品", "日用品", "書籍"]

    return pd.DataFrame(
        {
            "日付": pd.date_range("2020-01-01", periods=rows, freq="h"),
            "地域": np.random.choice(regions, rows),
            "商品名": np.random.choice(products, rows),
            "カテゴリ": np.random.choice(categories, rows),
            "売上": np.random.randint(100, 100000, rows),
            "数量": np.random.randint(1, 100, rows),
            "利益": np.random.randint(-10000, 50000, rows),
            "顧客ID": np.random.randint(1, 10000, rows),
        }
    )


def generate_large_csv_bytes(rows: int) -> bytes:
    """大規模CSVデータをバイト列で生成"""
    df = generate_large_dataframe(rows)
    buffer = StringIO()
    df.to_csv(buffer, index=False)
    return buffer.getvalue().encode("utf-8")


class TestDataProcessorPerformance:
    """DataProcessor の性能テスト"""

    @pytest.mark.parametrize("rows", [1000, 10000, 100000])
    def test_load_csv_performance(self, rows):
        """CSV読み込みの性能テスト"""
        csv_bytes = generate_large_csv_bytes(rows)
        processor = DataProcessor()

        start = time.perf_counter()
        df = processor.load_csv(csv_bytes)
        elapsed = time.perf_counter() - start

        assert len(df) == rows
        print(f"\n  load_csv ({rows:,} rows): {elapsed:.3f}s")

        # 性能基準: 10万行で5秒以内
        if rows == 100000:
            assert elapsed < 5.0, f"Too slow: {elapsed:.3f}s"

    @pytest.mark.parametrize("rows", [1000, 10000, 100000])
    def test_generate_summary_performance(self, rows):
        """サマリー生成の性能テスト"""
        df = generate_large_dataframe(rows)
        processor = DataProcessor()

        start = time.perf_counter()
        summary = processor.generate_summary(df)
        elapsed = time.perf_counter() - start

        assert summary["row_count"] == rows
        print(f"\n  generate_summary ({rows:,} rows): {elapsed:.3f}s")

        # 性能基準: 10万行で1秒以内
        if rows == 100000:
            assert elapsed < 1.0, f"Too slow: {elapsed:.3f}s"

    @pytest.mark.parametrize("rows", [1000, 10000, 100000])
    def test_calculate_statistics_performance(self, rows):
        """統計計算の性能テスト"""
        df = generate_large_dataframe(rows)
        processor = DataProcessor()

        start = time.perf_counter()
        stats = processor.calculate_statistics(df)
        elapsed = time.perf_counter() - start

        assert "売上" in stats
        print(f"\n  calculate_statistics ({rows:,} rows): {elapsed:.3f}s")

        # 性能基準: 10万行で2秒以内
        if rows == 100000:
            assert elapsed < 2.0, f"Too slow: {elapsed:.3f}s"


class TestAIGeneratorPerformance:
    """AIGenerator の性能テスト"""

    @pytest.mark.parametrize("rows", [1000, 10000, 100000])
    def test_execute_aggregation_performance(self, rows):
        """集計実行の性能テスト"""
        df = generate_large_dataframe(rows)

        py_code = """
def aggregate_all_data(df):
    import pandas as pd

    # KPI計算
    kpi = {
        "total_sales": int(df['売上'].sum()),
        "total_profit": int(df['利益'].sum()),
        "avg_sales": float(df['売上'].mean()),
        "transaction_count": len(df)
    }

    # グラフデータ
    charts = {
        "region_sales": df.groupby('地域')['売上'].sum().to_dict(),
        "category_sales": df.groupby('カテゴリ')['売上'].sum().to_dict(),
        "daily_sales": df.groupby(df['日付'].dt.date)['売上'].sum().head(30).to_dict()
    }

    return {"kpi": kpi, "charts": charts}
"""

        generator = AIGenerator(model=Mock())

        start = time.perf_counter()
        result = generator.execute_aggregation(py_code, df)
        elapsed = time.perf_counter() - start

        assert "kpi" in result
        assert result["kpi"]["transaction_count"] == rows
        print(f"\n  execute_aggregation ({rows:,} rows): {elapsed:.3f}s")

        # 性能基準: 10万行で3秒以内
        if rows == 100000:
            assert elapsed < 3.0, f"Too slow: {elapsed:.3f}s"


class TestChatHandlerPerformance:
    """ChatHandler の性能テスト"""

    @pytest.mark.parametrize("rows", [1000, 10000, 100000])
    def test_generate_chart_data_performance(self, rows):
        """グラフデータ生成の性能テスト"""
        df = generate_large_dataframe(rows)
        handler = ChatHandler(model=Mock())

        spec = {"type": "bar", "x": "地域", "y": "売上", "aggregation": "sum"}

        start = time.perf_counter()
        data = handler.generate_chart_data(spec, df)
        elapsed = time.perf_counter() - start

        assert len(data["labels"]) > 0
        print(f"\n  generate_chart_data ({rows:,} rows): {elapsed:.3f}s")

        # 性能基準: 10万行で1秒以内
        if rows == 100000:
            assert elapsed < 1.0, f"Too slow: {elapsed:.3f}s"

    @pytest.mark.parametrize("rows", [1000, 10000, 100000])
    def test_build_context_performance(self, rows):
        """コンテキスト構築の性能テスト"""
        df = generate_large_dataframe(rows)
        handler = ChatHandler(model=Mock())
        history = [{"role": "user", "content": f"Message {i}"} for i in range(100)]

        start = time.perf_counter()
        context = handler.build_context(df, history)
        elapsed = time.perf_counter() - start

        assert "data_summary" in context
        assert len(context["chat_history"]) == 10  # 直近10件に制限
        print(f"\n  build_context ({rows:,} rows): {elapsed:.3f}s")

        # 性能基準: 10万行で0.1秒以内
        if rows == 100000:
            assert elapsed < 0.1, f"Too slow: {elapsed:.3f}s"

    @pytest.mark.parametrize("rows", [1000, 10000, 100000])
    def test_get_data_info_performance(self, rows):
        """データ情報取得の性能テスト"""
        df = generate_large_dataframe(rows)
        handler = ChatHandler(model=Mock())

        start = time.perf_counter()
        info = handler._get_data_info(df)
        elapsed = time.perf_counter() - start

        assert "行数:" in info
        print(f"\n  _get_data_info ({rows:,} rows): {elapsed:.3f}s")

        # 性能基準: 10万行で1秒以内
        if rows == 100000:
            assert elapsed < 1.0, f"Too slow: {elapsed:.3f}s"


class TestMemoryUsage:
    """メモリ使用量のテスト"""

    def test_large_data_memory_footprint(self):
        """大規模データのメモリ使用量"""

        rows = 100000
        df = generate_large_dataframe(rows)

        # DataFrameのメモリ使用量
        memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
        print(f"\n  DataFrame ({rows:,} rows) memory: {memory_mb:.2f} MB")

        # 100万行で100MB以下を期待（8カラム）
        assert memory_mb < 100, f"Memory too high: {memory_mb:.2f} MB"


class TestEndToEndPerformance:
    """エンドツーエンド性能テスト"""

    def test_full_pipeline_performance(self):
        """完全なパイプラインの性能テスト"""
        rows = 50000
        csv_bytes = generate_large_csv_bytes(rows)

        # 1. CSV読み込み
        processor = DataProcessor()
        start = time.perf_counter()
        df = processor.load_csv(csv_bytes)
        load_time = time.perf_counter() - start

        # 2. サマリー生成
        start = time.perf_counter()
        summary = processor.generate_summary(df)
        summary_time = time.perf_counter() - start

        # 3. 統計計算
        start = time.perf_counter()
        stats = processor.calculate_statistics(df)
        stats_time = time.perf_counter() - start

        # 4. コンテキスト構築
        handler = ChatHandler(model=Mock())
        start = time.perf_counter()
        context = handler.build_context(df, [])
        context_time = time.perf_counter() - start

        total_time = load_time + summary_time + stats_time + context_time

        print(f"\n  === Full Pipeline ({rows:,} rows) ===")
        print(f"  CSV Load:    {load_time:.3f}s")
        print(f"  Summary:     {summary_time:.3f}s")
        print(f"  Statistics:  {stats_time:.3f}s")
        print(f"  Context:     {context_time:.3f}s")
        print(f"  TOTAL:       {total_time:.3f}s")

        # 全体で10秒以内
        assert total_time < 10.0, f"Pipeline too slow: {total_time:.3f}s"
