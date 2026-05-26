from app.schemas import Flashcard

DEFAULT_FLASHCARDS = [
    Flashcard(
        question="What HTTP method is typically used to create a resource?",
        answer="POST",
        domain="REST APIs",
    ),
    Flashcard(
        question="Which Python library is commonly used for HTTP requests?",
        answer="requests",
        domain="Python for Automation",
    ),
    Flashcard(
        question="What does JSON stand for?",
        answer="JavaScript Object Notation",
        domain="JSON/Data Modeling",
    ),
]


def get_flashcards(domain: str | None = None) -> list[Flashcard]:
    if not domain:
        return DEFAULT_FLASHCARDS
    return [card for card in DEFAULT_FLASHCARDS if card.domain.lower() == domain.lower()]
