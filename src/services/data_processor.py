"""
DataProcessor - CSV データの読み込みと処理

責務:
- CSVデータの読み込み（エンコーディング自動判定）
- データサマリーの生成
- 基本統計量の計算
"""

from io import StringIO
from typing import Any

import pandas as pd


class DataProcessor:
    """CSVデータの読み込みと基本的な処理を行うクラス"""

    SUPPORTED_ENCODINGS = ["utf-8", "shift_jis", "cp932", "euc-jp"]

    def load_csv(self, data: bytes) -> pd.DataFrame:
        """
        CSVデータを読み込む（エンコーディング自動判定）

        Args:
            data: CSVデータのバイト列

        Returns:
            pd.DataFrame: 読み込んだデータ

        Raises:
            ValueError: サポートされていないエンコーディングの場合
        """
        for encoding in self.SUPPORTED_ENCODINGS:
            try:
                text = data.decode(encoding)
                return pd.read_csv(StringIO(text))
            except (UnicodeDecodeError, UnicodeError):
                continue

        raise ValueError("サポートされていないエンコーディングです")

    def generate_summary(self, df: pd.DataFrame) -> dict[str, Any]:
        """
        データフレームのサマリーを生成する

        Args:
            df: 対象のDataFrame

        Returns:
            dict: サマリー情報
                - columns: カラム名リスト
                - row_count: 行数
                - sample_data: サンプルデータ（CSV文字列）
                - column_types: カラムの型情報
        """
        # カラムの型を分類
        numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
        categorical_columns = df.select_dtypes(include=["object"]).columns.tolist()

        # サンプルデータをCSV文字列に
        buffer = StringIO()
        df.head(5).to_csv(buffer, index=False)
        sample_csv = buffer.getvalue()

        return {
            "columns": df.columns.tolist(),
            "row_count": len(df),
            "sample_data": sample_csv,
            "column_types": {
                "numeric_columns": numeric_columns,
                "categorical_columns": categorical_columns,
            },
        }

    def calculate_statistics(self, df: pd.DataFrame) -> dict[str, Any]:
        """
        データフレームの統計情報を計算する

        Args:
            df: 対象のDataFrame

        Returns:
            dict: 各カラムの統計情報
                - 数値カラム: mean, sum, min, max, std
                - カテゴリカラム: value_counts, unique_count
        """
        stats = {}

        # 数値カラムの統計
        numeric_columns = df.select_dtypes(include=["number"]).columns
        for col in numeric_columns:
            stats[col] = {
                "mean": df[col].mean(),
                "sum": df[col].sum(),
                "min": df[col].min(),
                "max": df[col].max(),
                "std": df[col].std(),
            }

        # カテゴリカラムの統計
        categorical_columns = df.select_dtypes(include=["object"]).columns
        for col in categorical_columns:
            stats[col] = {
                "value_counts": df[col].value_counts().to_dict(),
                "unique_count": df[col].nunique(),
            }

        return stats
