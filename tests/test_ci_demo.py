# TEMPORARY: deliberately broken test, used only to see a red CI run on GitHub.
# This lives on the demo/failing-test branch and will be deleted afterwards.

from app.services.service import TextSummarizer


def test_this_will_fail_on_purpose():
    summarizer = TextSummarizer()

    result = summarizer.summarize("hello world")

    # The service returns "hello world"; we assert something else on purpose
    # so that GitHub Actions reports a failing test.
    assert result == "this is not what the summarizer returns"
