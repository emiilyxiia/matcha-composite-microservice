from fastapi import FastAPI
from src.routes.summary import router as summary_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Matcha Composite Service",
    version="0.1.0",
)

@app.get("/")
def root():
    return {
        "Welcome to the Matcha Drinking Tracker API. See /docs for OpenAPI UI."
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #we keep changing link so I keep it * for now, curr link: https://sprint2microservicewebapp.ue.r.appspot.com/
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(summary_router)
