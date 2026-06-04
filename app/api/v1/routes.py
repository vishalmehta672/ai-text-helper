from fastapi import APIRouter
from schemas.text import TextRequest  #  Correct path based on your sidebar

# 1. Define an APIRouter instance for this file
router = APIRouter()

# 3. Attach the endpoint to the router instead of 'app'
@router.post("/summarize")
def summarize_text(request: TextRequest):
    """
    Accepts a body with text and returns a static dummy summary.
    """
    return {"summary": "Dummy summary"}