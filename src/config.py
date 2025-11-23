import os

# get URLs from team and plug them into Cloud Run via environment variables.
USER_SERVICE_BASE_URL = os.getenv("USER_SERVICE_BASE_URL", "https://matcha-api-ktr6lb33ta-uc.a.run.app")
BUDGET_SERVICE_BASE_URL = os.getenv("BUDGET_SERVICE_BASE_URL", "http://localhost:8002")
RANKING_SERVICE_BASE_URL = os.getenv("RANKING_SERVICE_BASE_URL", "https://matchamania-rankings-api-945802238964.us-central1.run.app/")