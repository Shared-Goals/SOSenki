"""SOSenki FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.app.api.routes import miniapp

app = FastAPI(
    title="SOSenki API",
    description="Open-source Telegram Mini App for property management",
    version="0.1.0",
)

# Include routers
app.include_router(miniapp.router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


# TODO: Mount static frontend (when ready)
# app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
