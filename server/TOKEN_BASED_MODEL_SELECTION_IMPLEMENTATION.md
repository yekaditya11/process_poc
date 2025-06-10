# Token-Based Model Selection Implementation

## Overview
Implemented intelligent model selection based on a 16,000 token threshold to optimize speed and cost for both conversational AI and summarization functionality.

## Key Changes

### 1. Model Selection Logic
- **Under 16,000 tokens**: Use GPT-3.5-turbo (fastest, most cost-effective)
- **Over 16,000 tokens**: Use GPT-4o (large context, more capable)

### 2. Files Modified

#### `ai_summarizer/server/ai_engine/summarization_engine.py`
- Added tiktoken import for accurate token counting
- Implemented `_estimate_token_count()` method with tiktoken fallback
- Updated `_select_optimal_model()` method with 16k threshold logic
- Added separate model lists for fast vs large context models
- Updated model selection calls throughout the file

#### `ai_summarizer/server/ai_engine/conversational_ai.py`
- Added tiktoken import for accurate token counting
- Implemented `_estimate_token_count()` method with tiktoken fallback
- Added `_select_optimal_model()` method with 16k threshold logic
- Updated OpenAI API calls to use dynamic model selection
- Updated chart generation to prefer fast models

#### `ai_summarizer/server/api/web_api.py`
- Updated hardcoded GPT-4o references to use dynamic model selection
- Both insight generation endpoints now use optimal model selection

### 3. Model Configuration

#### Fast Models (< 16k tokens)
- `gpt-3.5-turbo` (primary choice for speed)
- `gpt-3.5-turbo-1106` (latest fast model)
- `gpt-3.5-turbo-16k` (fast with larger context)

#### Large Context Models (≥ 16k tokens)
- `gpt-4o` (primary choice for large contexts)
- `gpt-4o-mini` (faster large context option)
- `gpt-4-turbo-preview` (fallback large context)

### 4. Token Counting
- **Primary**: Uses tiktoken library for accurate token counting
- **Fallback**: Character-based estimation (1 token ≈ 4 characters)
- **Buffer**: Adds response token buffer (1500 for conversation, 2500 for summarization)

### 5. Performance Benefits
- **Speed**: Small requests use GPT-3.5-turbo (much faster response times)
- **Cost**: GPT-3.5-turbo is significantly cheaper than GPT-4o
- **Accuracy**: Large requests still use GPT-4o for complex analysis
- **Reliability**: Automatic fallback if tiktoken is unavailable

## Testing
Created comprehensive test suite (`test_token_based_model_selection.py`) that verifies:
- Token counting functionality
- Model selection logic for different prompt sizes
- Configuration correctness
- Threshold behavior

## Usage Examples

### Small Request (< 16k tokens)
```
User: "Show me incidents"
→ Estimated tokens: ~50
→ Selected model: gpt-3.5-turbo
→ Fast response, low cost
```

### Large Request (≥ 16k tokens)
```
User: Complex analysis with large data context
→ Estimated tokens: 18,000
→ Selected model: gpt-4o
→ Comprehensive analysis, higher cost but better quality
```

## Configuration
The 16,000 token threshold can be adjusted by modifying:
```python
self.token_threshold = 16000  # Adjust as needed
```

## Logging
The implementation includes detailed logging to track:
- Token count estimates
- Model selection decisions
- Threshold comparisons
- Performance metrics

## Backward Compatibility
- All existing functionality remains unchanged
- Automatic fallback to character-based counting if tiktoken unavailable
- Graceful degradation if model selection fails

## Future Enhancements
- Dynamic threshold adjustment based on response quality metrics
- Model performance monitoring and automatic optimization
- Cost tracking and budget-based model selection
- A/B testing framework for model comparison
