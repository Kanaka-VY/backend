from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes_chat import router as chat_router
from app.db.database import init_db
from app.core.config import settings

app = FastAPI(title="Ayra API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list(),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(chat_router)

@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def root():
    return {"message": "Ayra backend is running", "health": "/health", "chat_api": "/api/chat"}


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ayra-backend", "env": settings.app_env}