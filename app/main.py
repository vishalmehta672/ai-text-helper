from fastapi import FastAPI
from app.api.v1.routes import router as v1_router  # Import your router

app = FastAPI(
    title="Dummy Summarizer API",
    description="A simple API to test summarization endpoints without AI backend logic.",
    version="1.0.0"
)

# Include the routes from routes.py and give them a clean prefix
app.include_router(v1_router, prefix="/api/v1", tags=["Summarize"])