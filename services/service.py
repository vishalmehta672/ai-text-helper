class TextSummarizer:
    def summarize(self, text: str) -> str:
        # Logic: Extract first 20 words
        words = text.split()
        summary = " ".join(words[:20])
        return summary
    