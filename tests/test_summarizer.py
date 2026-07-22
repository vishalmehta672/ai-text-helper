import pytest

from app.services.service import TextSummarizer


def test_summarizer_returns_text():
    # Arrange
    summarizer = TextSummarizer()

    # Act
    result = summarizer.summarize("1234")

    # Assert
    assert isinstance(result, str)


def test_summarizer_handles_normal_paragraph():
    # Arrange: 25 numbered words so we can predict the exact truncation
    summarizer = TextSummarizer()
    words = [f"word{i}" for i in range(1, 26)]  # word1 ... word25
    text = " ".join(words)

    # Act
    result = summarizer.summarize(text)

    # Assert: only the first 20 words survive
    assert result == " ".join(words[:20])
    assert len(result.split()) == 20


def test_summarizer_handles_short_text():
    # Arrange: fewer than 20 words -> nothing should be truncated
    summarizer = TextSummarizer()
    text = "Short and simple input"

    # Act
    result = summarizer.summarize(text)

    # Assert: the whole input comes back unchanged
    assert result == text
    assert len(result.split()) == 4
    
    
def test_summarizer_rejects_empty_text():
    # Arrange: empty string is a valid str but has nothing to summarize.
    summarizer = TextSummarizer()

    # Act + Assert: we EXPECT a ValueError (right type, wrong value).
    with pytest.raises(ValueError):
        summarizer.summarize("")


def test_summarizer_rejects_whitespace_only_text():
    # Arrange: only spaces -> also nothing meaningful to summarize.
    summarizer = TextSummarizer()

    # Act + Assert
    with pytest.raises(ValueError):
        summarizer.summarize("     ")


def test_summarizer_rejects_none_input():
    # Arrange: None is not a str at all -> wrong TYPE.
    summarizer = TextSummarizer()

    # Act + Assert: we EXPECT a TypeError, NOT the messy AttributeError.
    with pytest.raises(TypeError):
        summarizer.summarize(None)  # type: ignore[arg-type]  # intentionally wrong type
        
        
