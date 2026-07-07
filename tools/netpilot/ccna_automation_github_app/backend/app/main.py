from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.db import get_connection, init_database, list_installations, list_recent_webhook_events
from app.github.auth import get_installation_access_token
from app.github.webhook import handle_webhook
from app.schemas import (
    Flashcard,
    PracticeQuestion,
    QuizResult,
    StudyPlanResponse,
    StudyProfile,
    WeakArea,
)
from app.services.flashcards import get_flashcards
from app.services.planner import build_study_plan
from app.services.practice_questions import get_practice_questions
from app.services.source_package import get_source_package
from app.services.weakness import detect_weak_areas

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_database(settings)
    yield


app = FastAPI(title="Automation Learning API", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/plan", response_model=StudyPlanResponse)
def generate_plan(profile: StudyProfile) -> StudyPlanResponse:
    return build_study_plan(profile)


@app.get("/api/flashcards", response_model=list[Flashcard])
def flashcards(domain: str | None = None) -> list[Flashcard]:
    return get_flashcards(domain)


@app.post("/api/weak-areas", response_model=list[WeakArea])
def weak_areas(results: list[QuizResult]) -> list[WeakArea]:
    return detect_weak_areas(results)


@app.get("/api/practice-questions", response_model=list[PracticeQuestion])
def practice_questions(domain: str | None = None) -> list[PracticeQuestion]:
    return get_practice_questions(domain)


@app.get("/api/source-package")
def source_package() -> dict:
    return get_source_package()


@app.get("/api/domains")
def domains() -> dict[str, list[str]]:
    with get_connection(settings) as conn:
        from app.db import list_domain_titles

        return {"domains": list_domain_titles(conn)}


@app.get("/api/github/status")
def github_status() -> dict[str, Any]:
    return {
        "configured": settings.github_configured,
        "app_id_set": bool(settings.github_app_id),
        "webhook_secret_set": bool(settings.github_webhook_secret),
        "private_key_set": bool(settings.load_github_private_key()),
    }


@app.get("/api/github/installations")
def github_installations() -> dict[str, Any]:
    with get_connection(settings) as conn:
        return {"installations": list_installations(conn)}


@app.get("/api/github/events")
def github_events(limit: int = 20) -> dict[str, Any]:
    limit = max(1, min(limit, 100))
    with get_connection(settings) as conn:
        return {"events": list_recent_webhook_events(conn, limit=limit)}


@app.post("/api/github/installations/{installation_id}/token")
def github_installation_token(installation_id: int) -> dict[str, Any]:
    if not settings.github_configured:
        raise HTTPException(status_code=503, detail="GitHub App is not configured")
    try:
        return get_installation_access_token(installation_id, settings)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/webhooks/github")
async def github_webhook(
    request: Request,
    x_github_event: str | None = Header(default=None, alias="X-GitHub-Event"),
    x_hub_signature_256: str | None = Header(default=None, alias="X-Hub-Signature-256"),
    x_github_delivery: str | None = Header(default=None, alias="X-GitHub-Delivery"),
) -> JSONResponse:
    body = await request.body()
    result = handle_webhook(
        body,
        event_type=x_github_event or "unknown",
        delivery_id=x_github_delivery,
        signature_header=x_hub_signature_256,
        settings=settings,
    )
    if not result.get("ok"):
        raise HTTPException(status_code=401, detail=result.get("error", "webhook rejected"))
    return JSONResponse(result)
