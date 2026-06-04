from pydantic import BaseModel, Field

class TextRequest(BaseModel):
    # You can even add validation rules here later, like requiring a minimum length
    text: str = Field(..., description="The raw text input that needs to be processed.")