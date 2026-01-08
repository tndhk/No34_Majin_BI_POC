"""
ChatHandler のテスト

責務:
- ユーザーメッセージの意図分類
- 質問応答
- 追加グラフ生成リクエスト処理
- コンテキスト管理
"""
import pytest
from unittest.mock import Mock, patch
import pandas as pd

from src.services.chat_handler import ChatHandler, ChatResponse, Intent


class TestChatHandlerIntentClassification:
    """意図分類機能のテスト"""

    def test_classify_question_intent(self):
        """質問の意図を分類できる"""
        mock_model = Mock()
        mock_model.generate_content.return_value = Mock(
            text='{"intent": "question", "entities": ["売上"]}'
        )

        handler = ChatHandler(model=mock_model)
        intent = handler.classify_intent("売上が一番高いのはどこ？")

        assert intent == Intent.QUESTION

    def test_classify_add_chart_intent(self):
        """グラフ追加リクエストの意図を分類できる"""
        mock_model = Mock()
        mock_model.generate_content.return_value = Mock(
            text='{"intent": "add_chart", "entities": ["地域別", "売上"]}'
        )

        handler = ChatHandler(model=mock_model)
        intent = handler.classify_intent("地域別の売上グラフを追加して")

        assert intent == Intent.ADD_CHART

    def test_classify_analyze_intent(self):
        """分析リクエストの意図を分類できる"""
        mock_model = Mock()
        mock_model.generate_content.return_value = Mock(
            text='{"intent": "analyze", "entities": ["東京", "大阪"]}'
        )

        handler = ChatHandler(model=mock_model)
        intent = handler.classify_intent("東京と大阪を比較して分析して")

        assert intent == Intent.ANALYZE

    def test_classify_summarize_intent(self):
        """まとめリクエストの意図を分類できる"""
        mock_model = Mock()
        mock_model.generate_content.return_value = Mock(
            text='{"intent": "summarize", "entities": []}'
        )

        handler = ChatHandler(model=mock_model)
        intent = handler.classify_intent("このデータをまとめて")

        assert intent == Intent.SUMMARIZE

    def test_classify_general_intent(self):
        """一般的な会話の意図を分類できる"""
        mock_model = Mock()
        mock_model.generate_content.return_value = Mock(
            text='{"intent": "general", "entities": []}'
        )

        handler = ChatHandler(model=mock_model)
        intent = handler.classify_intent("こんにちは")

        assert intent == Intent.GENERAL

    def test_classify_intent_fallback_on_invalid_json(self):
        """JSONパースエラー時はGENERALにフォールバック"""
        mock_model = Mock()
        mock_model.generate_content.return_value = Mock(
            text='これはJSONではありません'
        )

        handler = ChatHandler(model=mock_model)
        intent = handler.classify_intent("テスト")

        assert intent == Intent.GENERAL

    def test_classify_intent_fallback_on_invalid_intent(self):
        """不正なintent値の場合はGENERALにフォールバック"""
        mock_model = Mock()
        mock_model.generate_content.return_value = Mock(
            text='{"intent": "invalid_intent", "entities": []}'
        )

        handler = ChatHandler(model=mock_model)
        intent = handler.classify_intent("テスト")

        assert intent == Intent.GENERAL


class TestChatHandlerResponse:
    """応答生成機能のテスト"""

    def test_handle_message_returns_chat_response(self, sample_dataframe):
        """ChatResponseオブジェクトが返される"""
        mock_model = Mock()
        mock_model.generate_content.side_effect = [
            Mock(text='{"intent": "question", "entities": []}'),
            Mock(text="売上が最も高いのは大阪で、20000円です。")
        ]

        handler = ChatHandler(model=mock_model)
        context = {"df": sample_dataframe, "summary": {}}
        response = handler.handle_message("売上が一番高いのは？", context)

        assert isinstance(response, ChatResponse)

    def test_handle_question_returns_text_response(self, sample_dataframe):
        """質問に対してテキスト応答が返される"""
        mock_model = Mock()
        mock_model.generate_content.side_effect = [
            Mock(text='{"intent": "question", "entities": []}'),
            Mock(text="売上合計は65,000円です。")
        ]

        handler = ChatHandler(model=mock_model)
        context = {"df": sample_dataframe, "summary": {}}
        response = handler.handle_message("売上の合計は？", context)

        assert response.type == "text"
        assert response.content is not None

    def test_handle_add_chart_returns_chart_response(self, sample_dataframe):
        """グラフ追加リクエストに対してチャート応答が返される"""
        mock_model = Mock()
        mock_model.generate_content.side_effect = [
            Mock(text='{"intent": "add_chart", "entities": ["地域別"]}'),
            Mock(text="""地域別のグラフを作成しました。

```chart_spec
{"type": "bar", "title": "地域別売上", "x": "地域", "y": "売上"}
```
""")
        ]

        handler = ChatHandler(model=mock_model)
        context = {"df": sample_dataframe, "summary": {}}
        response = handler.handle_message("地域別のグラフを追加して", context)

        assert response.type == "chart"
        assert response.chart_spec is not None

    def test_handle_add_chart_with_invalid_chart_spec_json(self, sample_dataframe):
        """chart_specのJSONが不正な場合はNoneになる"""
        mock_model = Mock()
        mock_model.generate_content.side_effect = [
            Mock(text='{"intent": "add_chart", "entities": []}'),
            Mock(text="""グラフを作成しました。

```chart_spec
これは不正なJSON
```
""")
        ]

        handler = ChatHandler(model=mock_model)
        context = {"df": sample_dataframe, "summary": {}}
        response = handler.handle_message("グラフを追加", context)

        assert response.type == "chart"
        assert response.chart_spec is None

    def test_handle_analyze_returns_insight_response(self, sample_dataframe):
        """分析リクエストに対してインサイト応答が返される"""
        mock_model = Mock()
        mock_model.generate_content.side_effect = [
            Mock(text='{"intent": "analyze", "entities": []}'),
            Mock(text="分析結果: 東京と大阪で売上の80%を占めています。")
        ]

        handler = ChatHandler(model=mock_model)
        context = {"df": sample_dataframe, "summary": {}}
        response = handler.handle_message("地域ごとの傾向を分析して", context)

        assert response.type == "insight"

    def test_handle_summarize_returns_text_response(self, sample_dataframe):
        """まとめリクエストに対してテキスト応答が返される"""
        mock_model = Mock()
        mock_model.generate_content.side_effect = [
            Mock(text='{"intent": "summarize", "entities": []}'),
            Mock(text="データの要約: 5件のデータがあります。")
        ]

        handler = ChatHandler(model=mock_model)
        context = {"df": sample_dataframe, "summary": {}}
        response = handler.handle_message("このデータをまとめて", context)

        assert response.type == "text"
        assert "要約" in response.content or "データ" in response.content

    def test_handle_general_returns_text_response(self, sample_dataframe):
        """一般的な会話に対してテキスト応答が返される"""
        mock_model = Mock()
        mock_model.generate_content.side_effect = [
            Mock(text='{"intent": "general", "entities": []}'),
            Mock(text="こんにちは！データ分析のお手伝いをします。")
        ]

        handler = ChatHandler(model=mock_model)
        context = {"df": sample_dataframe, "summary": {}}
        response = handler.handle_message("こんにちは", context)

        assert response.type == "text"

    def test_handle_question_with_none_df(self):
        """dfがNoneの場合も処理できる"""
        mock_model = Mock()
        mock_model.generate_content.side_effect = [
            Mock(text='{"intent": "question", "entities": []}'),
            Mock(text="データがないため回答できません。")
        ]

        handler = ChatHandler(model=mock_model)
        context = {"df": None, "summary": {}}
        response = handler.handle_message("売上は？", context)

        assert response.type == "text"

    def test_handle_analyze_with_none_df(self):
        """dfがNoneの場合の分析処理"""
        mock_model = Mock()
        mock_model.generate_content.side_effect = [
            Mock(text='{"intent": "analyze", "entities": []}'),
            Mock(text="データがないため分析できません。")
        ]

        handler = ChatHandler(model=mock_model)
        context = {"df": None, "summary": {}}
        response = handler.handle_message("分析して", context)

        assert response.type == "insight"

    def test_handle_summarize_with_none_df(self):
        """dfがNoneの場合のまとめ処理"""
        mock_model = Mock()
        mock_model.generate_content.side_effect = [
            Mock(text='{"intent": "summarize", "entities": []}'),
            Mock(text="データがありません。")
        ]

        handler = ChatHandler(model=mock_model)
        context = {"df": None, "summary": {}}
        response = handler.handle_message("まとめて", context)

        assert response.type == "text"


class TestChatHandlerContext:
    """コンテキスト管理のテスト"""

    def test_build_context_includes_data_summary(self, sample_dataframe):
        """コンテキストにデータサマリーが含まれる"""
        handler = ChatHandler(model=Mock())
        context = handler.build_context(
            df=sample_dataframe,
            chat_history=[]
        )

        assert 'data_summary' in context
        assert '5' in context['data_summary']  # 行数

    def test_build_context_includes_column_info(self, sample_dataframe):
        """コンテキストにカラム情報が含まれる"""
        handler = ChatHandler(model=Mock())
        context = handler.build_context(
            df=sample_dataframe,
            chat_history=[]
        )

        assert 'columns' in context
        assert '売上' in context['columns']

    def test_build_context_includes_chat_history(self, sample_dataframe):
        """コンテキストに会話履歴が含まれる"""
        handler = ChatHandler(model=Mock())
        history = [
            {"role": "user", "content": "こんにちは"},
            {"role": "assistant", "content": "こんにちは！"}
        ]
        context = handler.build_context(
            df=sample_dataframe,
            chat_history=history
        )

        assert 'chat_history' in context
        assert len(context['chat_history']) == 2

    def test_build_context_limits_history(self, sample_dataframe):
        """会話履歴は直近10件に制限される"""
        handler = ChatHandler(model=Mock())
        history = [{"role": "user", "content": f"Message {i}"} for i in range(20)]

        context = handler.build_context(
            df=sample_dataframe,
            chat_history=history
        )

        assert len(context['chat_history']) == 10


class TestChatHandlerChartGeneration:
    """追加グラフ生成のテスト"""

    def test_generate_chart_spec_returns_dict(self, sample_dataframe):
        """グラフ仕様が辞書で返される"""
        mock_model = Mock()
        mock_model.generate_content.return_value = Mock(
            text='{"type": "bar", "title": "地域別売上", "x": "地域", "y": "売上"}'
        )

        handler = ChatHandler(model=mock_model)
        spec = handler.generate_chart_spec("地域別の売上", sample_dataframe.columns.tolist())

        assert isinstance(spec, dict)
        assert 'type' in spec
        assert 'title' in spec

    def test_generate_chart_spec_fallback_on_invalid_json(self, sample_dataframe):
        """JSONパースエラー時はデフォルト仕様を返す"""
        mock_model = Mock()
        mock_model.generate_content.return_value = Mock(
            text='これは不正なJSONです'
        )

        handler = ChatHandler(model=mock_model)
        columns = sample_dataframe.columns.tolist()
        spec = handler.generate_chart_spec("テスト", columns)

        assert spec['type'] == 'bar'
        assert spec['x'] == columns[0]
        assert spec['y'] == columns[1]

    def test_generate_chart_data_aggregates_correctly(self, sample_dataframe):
        """グラフデータが正しく集計される"""
        handler = ChatHandler(model=Mock())
        spec = {"type": "bar", "x": "地域", "y": "売上", "aggregation": "sum"}

        data = handler.generate_chart_data(spec, sample_dataframe)

        assert 'labels' in data
        assert 'values' in data
        assert '東京' in data['labels']

    def test_generate_chart_data_with_mean_aggregation(self, sample_dataframe):
        """mean集計が正しく動作する"""
        handler = ChatHandler(model=Mock())
        spec = {"type": "bar", "x": "地域", "y": "売上", "aggregation": "mean"}

        data = handler.generate_chart_data(spec, sample_dataframe)

        assert 'labels' in data
        assert 'values' in data

    def test_generate_chart_data_with_count_aggregation(self, sample_dataframe):
        """count集計が正しく動作する"""
        handler = ChatHandler(model=Mock())
        spec = {"type": "bar", "x": "地域", "y": "売上", "aggregation": "count"}

        data = handler.generate_chart_data(spec, sample_dataframe)

        assert 'labels' in data
        assert 'values' in data

    def test_generate_chart_data_with_unknown_aggregation(self, sample_dataframe):
        """不明な集計タイプはsumにフォールバック"""
        handler = ChatHandler(model=Mock())
        spec = {"type": "bar", "x": "地域", "y": "売上", "aggregation": "unknown"}

        data = handler.generate_chart_data(spec, sample_dataframe)

        assert 'labels' in data
        assert 'values' in data

    def test_generate_chart_data_with_invalid_columns(self, sample_dataframe):
        """存在しないカラムの場合は空リストを返す"""
        handler = ChatHandler(model=Mock())
        spec = {"type": "bar", "x": "存在しない", "y": "カラム", "aggregation": "sum"}

        data = handler.generate_chart_data(spec, sample_dataframe)

        assert data['labels'] == []
        assert data['values'] == []

    def test_generate_chart_html_returns_string(self, sample_dataframe):
        """グラフHTMLが文字列で返される"""
        handler = ChatHandler(model=Mock())
        spec = {"type": "bar", "title": "地域別売上", "x": "地域", "y": "売上"}
        data = {"labels": ["東京", "大阪"], "values": [22000, 35000]}

        html = handler.generate_chart_html(spec, data)

        assert isinstance(html, str)
        assert 'Chart' in html or 'chart' in html


class TestChatHandlerGetDataInfo:
    """_get_data_info メソッドのテスト"""

    def test_get_data_info_with_none(self):
        """Noneの場合は適切なメッセージを返す"""
        handler = ChatHandler(model=Mock())
        result = handler._get_data_info(None)

        assert result == "データがありません"

    def test_get_data_info_with_dataframe(self, sample_dataframe):
        """DataFrameの場合は統計情報を含む"""
        handler = ChatHandler(model=Mock())
        result = handler._get_data_info(sample_dataframe)

        assert "行数:" in result
        assert "カラム:" in result
        assert "売上" in result
