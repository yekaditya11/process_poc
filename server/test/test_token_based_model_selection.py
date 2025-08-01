"""
Test token-based model selection for AI engines
Tests the 16k token threshold implementation for GPT model selection
"""

import unittest
import sys
import os

# Add the server directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ai_engine.summarization_engine import SafetySummarizationEngine
from ai_engine.conversational_ai import ConversationalAI


class TestTokenBasedModelSelection(unittest.TestCase):
    """Test token-based model selection functionality"""

    def setUp(self):
        """Set up test fixtures"""
        # Initialize engines without OpenAI API key to test logic only
        self.summarization_engine = SafetySummarizationEngine(api_key=None)
        
        # Mock summarizer app for conversational AI
        class MockSummarizerApp:
            pass
        
        mock_app = MockSummarizerApp()
        self.conversational_ai = ConversationalAI(mock_app)

    def test_token_counting_fallback(self):
        """Test token counting fallback when tiktoken is not available"""
        # Test with summarization engine
        test_text = "This is a test message for token counting."
        token_count = self.summarization_engine._estimate_token_count(test_text)
        
        # Should return approximately len(text) // 4
        expected_count = len(test_text) // 4
        self.assertAlmostEqual(token_count, expected_count, delta=2)

    def test_model_selection_under_threshold(self):
        """Test model selection for prompts under 16k tokens"""
        # Create a small prompt (under 16k tokens)
        small_prompt = "What are the current safety incidents?" * 100  # ~400 tokens
        
        # Test summarization engine
        selected_model = self.summarization_engine._select_optimal_model(small_prompt)
        self.assertIn(selected_model, self.summarization_engine.fast_models)
        
        # Test conversational AI
        selected_model_conv = self.conversational_ai._select_optimal_model(small_prompt)
        self.assertIn(selected_model_conv, self.conversational_ai.fast_models)

    def test_model_selection_over_threshold(self):
        """Test model selection for prompts over 16k tokens"""
        # Create a large prompt (over 16k tokens)
        # Approximate 16k tokens = 64k characters
        large_prompt = "This is a very long safety analysis prompt. " * 1500  # ~60k+ characters
        
        # Test summarization engine
        selected_model = self.summarization_engine._select_optimal_model(large_prompt)
        self.assertIn(selected_model, self.summarization_engine.large_context_models)
        
        # Test conversational AI
        selected_model_conv = self.conversational_ai._select_optimal_model(large_prompt)
        self.assertIn(selected_model_conv, self.conversational_ai.large_context_models)

    def test_token_threshold_configuration(self):
        """Test that token threshold is correctly configured"""
        # Both engines should have the same 16k token threshold
        self.assertEqual(self.summarization_engine.token_threshold, 16000)
        self.assertEqual(self.conversational_ai.token_threshold, 16000)

    def test_fast_models_configuration(self):
        """Test that fast models are correctly configured"""
        expected_fast_models = [
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-1106", 
            "gpt-3.5-turbo-16k"
        ]
        
        self.assertEqual(self.summarization_engine.fast_models, expected_fast_models)
        self.assertEqual(self.conversational_ai.fast_models, expected_fast_models)

    def test_large_context_models_configuration(self):
        """Test that large context models are correctly configured"""
        expected_large_models = [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo-preview"
        ]
        
        self.assertEqual(self.summarization_engine.large_context_models, expected_large_models)
        self.assertEqual(self.conversational_ai.large_context_models, expected_large_models)

    def test_model_priority_logic(self):
        """Test that model selection prioritizes speed for small requests"""
        # Small prompt should select gpt-3.5-turbo (fastest)
        small_prompt = "Show me incidents"
        
        selected_model_sum = self.summarization_engine._select_optimal_model(small_prompt)
        selected_model_conv = self.conversational_ai._select_optimal_model(small_prompt)
        
        # Should select the first (fastest) model in fast_models list
        self.assertEqual(selected_model_sum, "gpt-3.5-turbo")
        self.assertEqual(selected_model_conv, "gpt-3.5-turbo")

    def test_buffer_calculation(self):
        """Test that response token buffer is correctly calculated"""
        test_prompt = "Test prompt"
        
        # Summarization engine uses 2500 token buffer
        sum_tokens = self.summarization_engine._estimate_token_count(test_prompt)
        # The method adds buffer internally, we can't directly test it but we can verify the logic
        
        # Conversational AI uses 1500 token buffer  
        conv_tokens = self.conversational_ai._estimate_token_count(test_prompt)
        
        # Both should return the same token count for the same text
        self.assertEqual(sum_tokens, conv_tokens)


if __name__ == '__main__':
    print("Testing token-based model selection...")
    print("=" * 50)
    
    # Run the tests
    unittest.main(verbosity=2)
