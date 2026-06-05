from fastapi import APIRouter, HTTPException

from schemas.text import SummaryResponse, TextRequest

router = APIRouter()

@router.post("/summarize", response_model=SummaryResponse)
async def summarize(request: TextRequest):
    # Logic: Validate "hi" case
    # Mocking the response
    return {
        "summary": "This is a summarized version of your provided text.",
        "metadata": {"word_count": 9, "model_version": "v1.0", "processing_time_ms": 50},
        "status": "success"
    }