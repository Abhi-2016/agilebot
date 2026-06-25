from fastapi import FastAPI
from app.api.teams import router as teams_router

app = FastAPI(title="AgileBot", version="0.1.0")

app.include_router(teams_router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "agilebot"}
