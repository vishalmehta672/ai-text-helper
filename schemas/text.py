from pydantic import BaseModel, Field
from typing import Optional

# Task 1: SummaryResponse Schema
class SummaryResponse(BaseModel):
    summary: str
    metadata: dict
    status: str

# Task 2: TextRequest with Validation
class TextRequest(BaseModel):
    # Enforces a minimum length of 10 characters to prevent invalid/empty input
    text: str = Field(..., min_length=10, description="The text to be summarized")