from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

app = FastAPI(title="Automation Learning API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+):5173",
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
