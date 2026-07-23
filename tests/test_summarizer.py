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


# ---------------------------------------------------------------------------
# Boundary tests: the limit is 20, so 20 and 21 are the risky numbers.
# ---------------------------------------------------------------------------

def test_summarizer_keeps_exactly_twenty_words():
    # Arrange: exactly at the limit -> nothing should be cut.
    summarizer = TextSummarizer()
    words = [f"word{i}" for i in range(1, 21)]  # word1 ... word20
    text = " ".join(words)

    # Act
    result = summarizer.summarize(text)

    # Assert: all 20 survive, untouched
    assert result == text
    assert len(result.split()) == 20


def test_summarizer_drops_the_twenty_first_word():
    # Arrange: one word over the limit -> exactly one word must disappear.
    summarizer = TextSummarizer()
    words = [f"word{i}" for i in range(1, 22)]  # word1 ... word21
    text = " ".join(words)

    # Act
    result = summarizer.summarize(text)

    # Assert
    assert len(result.split()) == 20
    assert result.endswith("word20")
    assert "word21" not in result


# ---------------------------------------------------------------------------
# Documenting existing behaviour: split()/join() collapses all whitespace.
# ---------------------------------------------------------------------------

def test_summarizer_collapses_extra_spaces():
    # Arrange
    summarizer = TextSummarizer()

    # Act
    result = summarizer.summarize("hello     world")

    # Assert: many spaces become a single space
    assert result == "hello world"


def test_summarizer_collapses_newlines_and_tabs():
    # Arrange: real-world pasted text often contains \n and \t
    summarizer = TextSummarizer()

    # Act
    result = summarizer.summarize("hello\nworld\tagain")

    # Assert: every whitespace kind becomes a single space
    assert result == "hello world again"


def test_summarizer_strips_surrounding_whitespace():
    # Arrange
    summarizer = TextSummarizer()

    # Act
    result = summarizer.summarize("   hello world   ")

    # Assert: leading/trailing whitespace is gone
    assert result == "hello world"


# ---------------------------------------------------------------------------
# One test, many inputs: @parametrize runs the body once per value.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "bad_input",
    [
        None,
        123,
        4.5,
        ["a", "list"],
        {"a": "dict"},
    ],
)
def test_summarizer_rejects_every_non_string_type(bad_input):
    # Arrange
    summarizer = TextSummarizer()

    # Act + Assert: each of these is the wrong TYPE
    with pytest.raises(TypeError):
        summarizer.summarize(bad_input)


# ---------------------------------------------------------------------------
# Checking the error MESSAGE, not just the error type.
# ---------------------------------------------------------------------------

def test_type_error_message_names_the_offending_type():
    # Arrange
    summarizer = TextSummarizer()

    # Act: capture the exception object via `as exc_info`
    with pytest.raises(TypeError) as exc_info:
        summarizer.summarize(123)  # type: ignore[arg-type]

    # Assert: OUTSIDE the with-block, inspect the captured error
    assert "int" in str(exc_info.value)


def test_value_error_message_explains_the_problem():
    # Arrange
    summarizer = TextSummarizer()

    # Act
    with pytest.raises(ValueError) as exc_info:
        summarizer.summarize("")

    # Assert
    assert "empty" in str(exc_info.value)
