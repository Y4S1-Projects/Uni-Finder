# main.py
from fastapi import FastAPI
from app.api.recommend import router as recommend_router
from app.core.logging import setup_logging

def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title="UniFinder Degree Recommendation Service",
        version="1.0.0",
        description="AI-based degree recommendation engine for Sri Lankan students"
    )

    app.include_router(recommend_router, prefix="/recommend", tags=["Recommendation"])

    @app.get("/health", tags=["Health"])
    def health_check():
        return {"status": "ok"}

    return app


app = create_app()
