from pydantic import BaseModel, Field


class StudyProfile(BaseModel):
    exam_date: str = Field(..., description="Target exam date (YYYY-MM-DD)")
    hours_per_week: int = Field(..., ge=1, le=80)
    current_level: str = Field(default="beginner")


class QuizResult(BaseModel):
    domain: str
    score_percent: float = Field(..., ge=0, le=100)
    attempts: int = Field(default=1, ge=1)


class StudyPlanWeek(BaseModel):
    week: int
    focus_domains: list[str]
    goals: list[str]


class StudyPlanResponse(BaseModel):
    summary: str
    weekly_plan: list[StudyPlanWeek]


class Flashcard(BaseModel):
    question: str
    answer: str
    domain: str


class WeakArea(BaseModel):
    domain: str
    weakness_score: float
    recommendation: str


class PracticeQuestion(BaseModel):
    prompt: str
    options: list[str]
    correct_option_index: int = Field(..., ge=0)
    explanation: str
    distractor_rationales: list[str] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)
    domain: str
    source: str
    policy_note: str
