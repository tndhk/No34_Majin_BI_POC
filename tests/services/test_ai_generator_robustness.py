
import pytest
from unittest.mock import Mock
from src.services.ai_generator import AIGenerator

class TestAIGeneratorRobustness:
    """AIGeneratorの堅牢性テスト"""

    @pytest.fixture
    def generator(self):
        return AIGenerator(model=Mock())

    def test_assemble_html_standard_placeholder(self, generator):
        """標準的なプレースホルダー {{JSON_DATA}} の置換"""
        template = "<script>const dashboardData = {{JSON_DATA}};</script>"
        data = {"key": "value"}
        result = generator.assemble_html(template, data)
        assert 'const dashboardData = {"key": "value"};' in result

    def test_assemble_html_spaced_placeholder(self, generator):
        """空白を含むプレースホルダー {{ JSON_DATA }} の置換"""
        template = "<script>const dashboardData = {{  JSON_DATA  }};</script>"
        data = {"key": "value"}
        result = generator.assemble_html(template, data)
        assert 'const dashboardData = {"key": "value"};' in result

    def test_assemble_html_fallback_replacement(self, generator):
        """プレースホルダーがなく、変数が定義されている場合の置換"""
        template = "<script>const dashboardData = {};</script>"
        data = {"key": "value"}
        result = generator.assemble_html(template, data)
        assert 'const dashboardData = {"key": "value"};' in result

    def test_assemble_html_injection_fallback(self, generator):
        """プレースホルダーも変数定義もない場合の強制挿入"""
        template = "<html><body><h1>Test</h1></body></html>"
        data = {"key": "value"}
        result = generator.assemble_html(template, data)
        assert '<script>const dashboardData = {"key": "value"};</script>' in result
        assert "</body>" in result

