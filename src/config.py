import os

def env(name: str, default: str | None = None) -> str | None:
    return os.getenv(name, default)

#local dev URLs:
USER_SERVICE_BASE_URL = env("USER_SERVICE_BASE_URL","https://matcha-api-ktr6lb33ta-uc.a.run.app")

BUDGET_SERVICE_BASE_URL = env("BUDGET_SERVICE_BASE_URL","http://136.110.166.166")

RANKING_SERVICE_BASE_URL = env("RANKING_SERVICE_BASE_URL","https://matchamania-rankings-api-945802238964.us-central1.run.app")

#JWT Config:
JWT_SECRET = env("JWT_SECRET", "dev-only-secret")  # overrides in Cloud Run
JWT_ALGORITHM = env("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(env("JWT_EXPIRE_MINUTES", "60"))

#Google Auth
GOOGLE_CLIENT_ID = env(
    "GOOGLE_CLIENT_ID",
    ""
)


'''Setting env for cloud run:
gcloud run services update matcha-composite-service \
  --region us-central1 \
  --set-env-vars \
JWT_SECRET="cloud-run-secret",\
USER_SERVICE_BASE_URL="https://matcha-api-ktr6lb33ta-uc.a.run.app",\
BUDGET_SERVICE_BASE_URL="http://136.110.166.166",\
RANKING_SERVICE_BASE_URL="https://matchamania-rankings-api-945802238964.us-central1.run.app"
'''