from app.schemas import StudyPlanResponse, StudyPlanWeek, StudyProfile


def build_study_plan(profile: StudyProfile) -> StudyPlanResponse:
    hours = profile.hours_per_week

    weekly_plan = [
        StudyPlanWeek(
            week=1,
            focus_domains=["Python for Automation", "REST APIs"],
            goals=[
                f"Complete {max(2, hours // 3)} automation lessons",
                "Build one API-driven network task",
            ],
        ),
        StudyPlanWeek(
            week=2,
            focus_domains=["JSON/Data Modeling", "Network Fundamentals"],
            goals=[
                "Practice payload parsing and validation",
                "Run domain quiz and review weak areas",
            ],
        ),
        StudyPlanWeek(
            week=3,
            focus_domains=["Cisco Controller Concepts", "Troubleshooting Workflows"],
            goals=[
                "Complete controller workflow lab",
                "Simulate automation failure + rollback",
            ],
        ),
        StudyPlanWeek(
            week=4,
            focus_domains=["Hands-on Review"],
            goals=[
                "Run a full timed practice session",
                "Review flashcards for weak automation domains",
            ],
        ),
    ]

    return StudyPlanResponse(
        summary=f"4-week automation skills plan based on {hours} hrs/week.",
        weekly_plan=weekly_plan,
    )
