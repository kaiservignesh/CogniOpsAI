# Application entry point
from fastapi import FastAPI

app = FastAPI(
    title="CogniOps AI",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "CogniOps AI Backend is running"}

@app.get("/health")
def health():
    return {"status": "Healthy"}