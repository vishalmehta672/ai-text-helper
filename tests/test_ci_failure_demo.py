# TEMPORARY FILE - deliberately failing tests, added only to watch GitHub
# Actions turn red. Delete this file (and revert the commit) afterwards.

import pytest

from app.services.service import TextSummarizer


def test_demo_wrong_expected_value():
    """Failure style 1: the assert compares against the wrong string."""
    summarizer = TextSummarizer()

    result = summarizer.summarize("hello world")

    assert result == "THIS IS WRONG ON PURPOSE"


def test_demo_wrong_word_count():
    """Failure style 2: numbers don't match, pytest shows both sides."""
    summarizer = TextSummarizer()
    words = [f"word{i}" for i in range(1, 26)]  # 25 words

    result = summarizer.summarize(" ".join(words))

    assert len(result.split()) == 25  # WRONG: it truncates to 20


def test_demo_expected_error_never_raised():
    """Failure style 3: we demand an error, the code succeeds instead."""
    summarizer = TextSummarizer()

    with pytest.raises(ValueError):
        summarizer.summarize("this text is perfectly valid")
