# main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.recommend import router as recommend_router
from app.api.courses import router as courses_router
from app.core.logging import setup_logging


def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title="UniFinder Degree Recommendation Service",
        version="1.0.0",
        description="AI-based degree recommendation engine for Sri Lankan students",
    )

    default_origins = ",".join(
        [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
    )
    allowed_origins = (os.getenv("CORS_ORIGINS") or default_origins).split(",")
    allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(recommend_router, prefix="/recommend", tags=["Recommendation"])
    app.include_router(courses_router, prefix="/api", tags=["Courses"])

    @app.get("/health", tags=["Health"])
    def health_check():
        return {"status": "ok"}

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "5001"))
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=True)
