import uvicorn

from app.core.config import settings


if __name__ == "__main__":
    # Always run locally on the standardized port (5001).
    # This avoids uvicorn CLI's default port (8000).
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=int(getattr(settings, "PORT", 5001)),
        reload=True,
    )
