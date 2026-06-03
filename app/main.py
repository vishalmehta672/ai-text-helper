from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "AI Text Helper API is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}