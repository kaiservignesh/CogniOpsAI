# Application entry point
from app.api.user import router as user_router
from app.auth.router import router as auth_router
from app.core.logger import logger
from fastapi import FastAPI

logger.info("CogniOps AI started successfully")



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

app.include_router(user_router)
app.include_router(auth_router)