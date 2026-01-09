import unittest

import pandas as pd

from src.services.mock_generator import MockAIGenerator


class TestMockAIGenerator(unittest.TestCase):
    """
    Test cases for MockAIGenerator based on the Test Perspective Table.
    """

    def setUp(self):
        self.generator = MockAIGenerator()

    def test_mock_01_normal_input(self):
        """
        TC-MOCK-01: Valid DataFrame input
        Perspective: Equivalence – Normal
        """
        # Given: A valid DataFrame
        df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})

        # When: generate_oneshot is called
        result = self.generator.generate_oneshot(df)

        # Then: Returns valid GenerationResult
        self.assertIsNotNone(result.html)
        self.assertIsNotNone(result.data)
        self.assertIsInstance(result.data, dict)
        self.assertIn("<!DOCTYPE html>", result.html)

    def test_mock_02_none_input(self):
        """
        TC-MOCK-02: None input
        Perspective: Boundary – NULL input
        """
        # Given: None as input
        df = None

        # When: generate_oneshot is called
        result = self.generator.generate_oneshot(df)

        # Then: Returns valid mock result (no error)
        self.assertIsInstance(result.data, dict)
        self.assertIn("kpi", result.data)

    def test_mock_03_empty_dataframe(self):
        """
        TC-MOCK-03: Empty DataFrame input
        Perspective: Boundary – Empty input
        """
        # Given: Empty DataFrame
        df = pd.DataFrame()

        # When: generate_oneshot is called
        result = self.generator.generate_oneshot(df)

        # Then: Returns valid mock result (no error)
        self.assertIsInstance(result.data, dict)
        self.assertIn("kpi", result.data)

    def test_mock_04_data_integrity(self):
        """
        TC-MOCK-04: Mock Data Structure
        Perspective: Data Integrity
        """
        # Given: Any input
        df = pd.DataFrame({"a": [1]})

        # When: generate_oneshot is called
        result = self.generator.generate_oneshot(df)

        # Then: Keys `kpi`, `charts`, `insight_summary` exist
        self.assertIn("kpi", result.data)
        self.assertIn("charts", result.data)
        self.assertIn("insight_summary", result.data)

        # Check specific mock data values (contract verification)
        self.assertEqual(result.data["kpi"]["total_passengers"], 891)
        self.assertIn("survival_by_class", result.data["charts"])

    def test_mock_05_generated_html_content(self):
        """
        TC-MOCK-05: Generated HTML Content
        Perspective: Output Content
        """
        # Given: Any input
        df = pd.DataFrame({"a": [1]})

        # When: generate_oneshot is called
        result = self.generator.generate_oneshot(df)

        # Then: Contains "Demo Mode" and injected JSON
        self.assertIn("Demo Mode", result.html)
        # Verify JSON injection worked
        # We check if a known unique value from mock_data is present in html
        self.assertIn("38.4%", result.html)  # survival_rate value

    def test_mock_06_progress_callback(self):
        """
        TC-MOCK-06: Progress Callback
        Perspective: Functional
        """
        # Given: A mock callback
        progress_updates = []

        def mock_callback(step: int, message: str):
            progress_updates.append((step, message))

        # When: generate_oneshot is called with callback
        self.generator.generate_oneshot(pd.DataFrame(), progress_callback=mock_callback)

        # Then: Callback is called
        self.assertGreater(len(progress_updates), 0)
        self.assertEqual(progress_updates[0][0], 1)


if __name__ == "__main__":
    unittest.main()
