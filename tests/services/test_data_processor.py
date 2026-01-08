"""
DataProcessor のテスト

責務:
- CSVデータの読み込み（エンコーディング自動判定）
- データサマリーの生成
- 基本統計量の計算
"""
import pytest
import pandas as pd
from io import BytesIO

from src.services.data_processor import DataProcessor


class TestDataProcessorLoadCSV:
    """CSV読み込み機能のテスト"""

    def test_load_csv_utf8(self, sample_csv_utf8):
        """UTF-8のCSVを読み込める"""
        processor = DataProcessor()
        df = processor.load_csv(sample_csv_utf8.encode('utf-8'))

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 5
        assert list(df.columns) == ['日付', '商品名', '売上', '地域']

    def test_load_csv_shiftjis(self, sample_csv_shiftjis):
        """Shift_JISのCSVを読み込める（自動判定）"""
        processor = DataProcessor()
        df = processor.load_csv(sample_csv_shiftjis)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 5
        assert '商品名' in df.columns  # 日本語カラムが正しく読める

    def test_load_csv_returns_all_rows(self, sample_csv_utf8):
        """全行を読み込む"""
        processor = DataProcessor()
        df = processor.load_csv(sample_csv_utf8.encode('utf-8'))

        assert len(df) == 5


class TestDataProcessorSummary:
    """データサマリー生成機能のテスト"""

    def test_generate_summary_returns_dict(self, sample_dataframe):
        """サマリーが辞書で返される"""
        processor = DataProcessor()
        summary = processor.generate_summary(sample_dataframe)

        assert isinstance(summary, dict)

    def test_generate_summary_contains_columns(self, sample_dataframe):
        """サマリーにカラム情報が含まれる"""
        processor = DataProcessor()
        summary = processor.generate_summary(sample_dataframe)

        assert 'columns' in summary
        assert summary['columns'] == ['日付', '商品名', '売上', '地域']

    def test_generate_summary_contains_row_count(self, sample_dataframe):
        """サマリーに行数が含まれる"""
        processor = DataProcessor()
        summary = processor.generate_summary(sample_dataframe)

        assert 'row_count' in summary
        assert summary['row_count'] == 5

    def test_generate_summary_contains_sample_data(self, sample_dataframe):
        """サマリーにサンプルデータ（5行）が含まれる"""
        processor = DataProcessor()
        summary = processor.generate_summary(sample_dataframe)

        assert 'sample_data' in summary
        assert isinstance(summary['sample_data'], str)

    def test_generate_summary_contains_column_types(self, sample_dataframe):
        """サマリーにカラムの型情報が含まれる"""
        processor = DataProcessor()
        summary = processor.generate_summary(sample_dataframe)

        assert 'column_types' in summary
        assert 'numeric_columns' in summary['column_types']
        assert 'categorical_columns' in summary['column_types']


class TestDataProcessorStatistics:
    """統計情報計算機能のテスト"""

    def test_calculate_statistics_returns_dict(self, sample_dataframe):
        """統計情報が辞書で返される"""
        processor = DataProcessor()
        stats = processor.calculate_statistics(sample_dataframe)

        assert isinstance(stats, dict)

    def test_calculate_statistics_numeric_columns(self, sample_dataframe):
        """数値カラムの統計が計算される"""
        processor = DataProcessor()
        stats = processor.calculate_statistics(sample_dataframe)

        assert '売上' in stats
        assert 'mean' in stats['売上']
        assert 'sum' in stats['売上']
        assert 'min' in stats['売上']
        assert 'max' in stats['売上']

    def test_calculate_statistics_values(self, sample_dataframe):
        """統計値が正しく計算される"""
        processor = DataProcessor()
        stats = processor.calculate_statistics(sample_dataframe)

        assert stats['売上']['sum'] == 65000  # 10000+15000+12000+8000+20000
        assert stats['売上']['min'] == 8000
        assert stats['売上']['max'] == 20000
        assert stats['売上']['mean'] == 13000  # 65000/5

    def test_calculate_statistics_categorical_counts(self, sample_dataframe):
        """カテゴリカラムの値カウントが計算される"""
        processor = DataProcessor()
        stats = processor.calculate_statistics(sample_dataframe)

        assert '地域' in stats
        assert 'value_counts' in stats['地域']
        assert stats['地域']['value_counts']['東京'] == 2
        assert stats['地域']['value_counts']['大阪'] == 2
