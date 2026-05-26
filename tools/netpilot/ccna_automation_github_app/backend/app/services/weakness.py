from app.schemas import QuizResult, WeakArea


def detect_weak_areas(results: list[QuizResult]) -> list[WeakArea]:
    weak_areas: list[WeakArea] = []

    for result in results:
        weakness_score = round(max(0.0, (100 - result.score_percent) / 100), 2)
        if weakness_score >= 0.3:
            weak_areas.append(
                WeakArea(
                    domain=result.domain,
                    weakness_score=weakness_score,
                    recommendation=f"Review {result.domain} flashcards and retake a focused quiz.",
                )
            )

    return sorted(weak_areas, key=lambda w: w.weakness_score, reverse=True)
