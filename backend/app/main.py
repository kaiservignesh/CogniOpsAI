# Application entry point
from app.alerts.router import router as alert_router
from app.api.situation import router as situation_router
from app.api.user import router as user_router
from app.auth.router import router as auth_router
from app.core.logger import logger
from app.integrations.router import router as integration_router
from app.api.correlation import router as correlation_router
from app.api.ai import router as ai_router
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
app.include_router(alert_router)
app.include_router(integration_router)
app.include_router(situation_router)
app.include_router(correlation_router)
app.include_router(ai_router)