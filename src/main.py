from fastapi import FastAPI
from src.routes.summary import router as summary_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Matcha Composite Service",
    version="0.1.0",
)

app.include_router(summary_router)

@app.get("/health")
def health():
    return {"status": "ok"}