from app.core.logger import logger
class TextSummarizer:
    def summarize(self, text: str) -> str:
        logger.info("Request received")

        # Guard 1 (fail fast): reject wrong TYPE before doing any work.
        # None, ints, lists etc. would otherwise crash later with a confusing
        # AttributeError on .split(); we surface a clean TypeError instead.
        if not isinstance(text, str):
            logger.error(f"Invalid input type: expected str, got {type(text).__name__}")
            raise TypeError(f"text must be a str, got {type(text).__name__}")

        # Guard 2: correct type but empty/whitespace-only VALUE -> nothing to summarize.
        if not text.strip():
            logger.error("Invalid input value: text is empty or whitespace-only")
            raise ValueError("text must not be empty")

        logger.info("Summary generation started")
        # Logic: Extract first 20 words
        words = text.split()
        summary = " ".join(words[:20])
        logger.info("Summary generated successfully")
        return summary
