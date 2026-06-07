from fastapi import APIRouter

from schemas.text import SummaryResponse, TextRequest
from services.service import TextSummarizer
router = APIRouter()

summarizer_service = TextSummarizer()

@router.post("/summarize", response_model=SummaryResponse)
async def summarize(request: TextRequest):
    summary_text = summarizer_service.summarize(request.text)
    
    return {
        "summary": summary_text,
        "metadata": {"word_count": len(summary_text.split()), "model_version": "v1.0"},
        "status": "success"
    }