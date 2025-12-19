from fastapi import FastAPI
from src.routes.summary import router as summary_router
from fastapi.middleware.cors import CORSMiddleware
from src.routes.auth import router as auth_router
from fastapi.security import HTTPBearer

security = HTTPBearer()

app = FastAPI(
    title="Matcha Summary - Composite Microservice",
    version="1.0.0",
)

@app.get("/")
def root():
    return {
       "message": "Welcome to the Matcha Composite Service. See /docs for API documentation."
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #we keep changing link so I keep it * for now, curr link: https://sprint2microservicewebapp.ue.r.appspot.com/
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(summary_router)
app.include_router(auth_router)