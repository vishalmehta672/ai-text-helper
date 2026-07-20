from app.core.logger import logger
class TextSummarizer:
    def summarize(self, text: str) -> str:
        logger.info("Request received")
        logger.info("Summary generation started")
        # Logic: Extract first 20 words
        words = text.split()
        summary = " ".join(words[:20])
        logger.info("Summary generated successfully")
        return summary
