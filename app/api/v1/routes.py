from fastapi import APIRouter, HTTPException

from app.core.logger import logger
from app.schemas.text import SummaryResponse, TextRequest
from app.services.service import TextSummarizer
router = APIRouter()

summarizer_service = TextSummarizer()

@router.post("/summarize", response_model=SummaryResponse)
async def summarize(request: TextRequest):
    try:
        summary_text = summarizer_service.summarize(request.text)
    except Exception as e:
        logger.error(f"Summarization failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate summary")

    return {
        "summary": summary_text,
        "metadata": {"word_count": len(summary_text.split()), "model_version": "v1.0"},
        "status": "success"
    }