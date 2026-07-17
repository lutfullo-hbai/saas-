from fastapi import FastAPI

app = FastAPI(
    title="Disipl API",
    description="AI-Powered Personal Discipline & Goal Execution System",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "disipl"}
