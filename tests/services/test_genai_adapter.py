from unittest.mock import Mock
from src.services.genai_adapter import GenAIModelAdapter, GenAIResponse, _extract_text

class TestGenAIAdapter:
    """GenAIModelAdapter のテスト"""

    def test_generate_content_success(self):
        # Given: Mock client that returns a valid response
        # Perspective: GEN-N-01 (Equivalence - Normal)
        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = "AI Result"
        mock_client.models.generate_content.return_value = mock_response
        
        adapter = GenAIModelAdapter(client=mock_client, model_name="gemini-2.0-flash")
        
        # When: Generating content
        resp = adapter.generate_content("Hello")
        
        # Then: Returns GenAIResponse with correct text
        assert isinstance(resp, GenAIResponse)
        assert resp.text == "AI Result"

    def test_generate_content_fallback_extraction(self):
        # Given: Mock response lacking .text but having candidates
        # Perspective: GEN-A-01 (Equivalence - Fallback)
        mock_client = Mock()
        
        # setup candidate structure
        part = Mock()
        part.text = "Extracted Text"
        candidate = Mock()
        candidate.content.parts = [part]
        
        mock_response = Mock(spec=["candidates"])
        mock_response.candidates = [candidate]
        del mock_response.text # ensure .text is missing
        
        mock_client.models.generate_content.return_value = mock_response
        
        adapter = GenAIModelAdapter(client=mock_client, model_name="gemini-2.0-flash")
        
        # When: Generating content
        resp = adapter.generate_content("Hello")
        
        # Then: Text extracted via _extract_text fallback
        assert resp.text == "Extracted Text"

    def test_extract_text_empty_candidates(self):
        # Given: Response with empty candidates
        # Perspective: GEN-B-01 (Boundary - Empty)
        mock_response = Mock()
        mock_response.candidates = []
        
        # When: Extracting
        text = _extract_text(mock_response)
        
        # Then: Returns empty string
        assert text == ""

    def test_extract_text_no_parts(self):
        # Given: Candidate with no parts
        mock_response = Mock()
        candidate = Mock()
        candidate.content.parts = None
        mock_response.candidates = [candidate]
        
        # When: Extracting
        text = _extract_text(mock_response)
        
        # Then: Returns empty string
        assert text == ""
