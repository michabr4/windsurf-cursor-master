"""SQLite persistence: schema, seed data, and query helpers."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator

import yaml

from app.config import DOMAIN_MAP_PATH, SCHEMA_PATH, SEED_PATH, Settings, get_settings

DOMAIN_TITLE_ALIASES: dict[str, str] = {
    "Python for Automation": "Python for Automation",
    "REST APIs": "REST APIs",
    "JSON/Data Modeling": "JSON/Data Modeling",
    "Cisco Controller Concepts": "Cisco Controller Concepts",
    "Troubleshooting Workflows": "Troubleshooting Workflows",
    "Network Fundamentals": "Troubleshooting Workflows",
    "Hands-on Review": "Troubleshooting Workflows",
}


def _connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_connection(settings: Settings | None = None) -> Generator[sqlite3.Connection, None, None]:
    settings = settings or get_settings()
    conn = _connect(settings.database_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _meta_get(conn: sqlite3.Connection, key: str) -> str | None:
    row = conn.execute("SELECT value FROM app_meta WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else None


def _meta_set(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        "INSERT INTO app_meta (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )


def init_database(settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    with get_connection(settings) as conn:
        conn.executescript(schema_sql)
        if _meta_get(conn, "seed_version") != "2":
            _seed_all(conn)
            _meta_set(conn, "seed_version", "2")


def _seed_domains(conn: sqlite3.Connection) -> dict[str, int]:
    code_to_id: dict[str, int] = {}
    if not DOMAIN_MAP_PATH.is_file():
        return code_to_id
    data = yaml.safe_load(DOMAIN_MAP_PATH.read_text(encoding="utf-8")) or {}
    for item in data.get("domains", []):
        code = item["code"]
        title = item["title"]
        conn.execute(
            "INSERT OR IGNORE INTO domains (code, title) VALUES (?, ?)",
            (code, title),
        )
        row = conn.execute("SELECT id FROM domains WHERE code = ?", (code,)).fetchone()
        if row:
            code_to_id[code] = int(row["id"])
            code_to_id[title] = int(row["id"])
    return code_to_id


def _resolve_domain_id(conn: sqlite3.Connection, domain_label: str, code_to_id: dict[str, int]) -> int | None:
    if domain_label in code_to_id:
        return code_to_id[domain_label]
    alias = DOMAIN_TITLE_ALIASES.get(domain_label, domain_label)
    if alias in code_to_id:
        return code_to_id[alias]
    row = conn.execute(
        "SELECT id FROM domains WHERE title = ? OR code = ?",
        (domain_label, domain_label),
    ).fetchone()
    if row:
        return int(row["id"])
    conn.execute(
        "INSERT INTO domains (code, title) VALUES (?, ?)",
        (domain_label.lower().replace(" ", "_")[:32], domain_label),
    )
    row = conn.execute("SELECT id FROM domains WHERE title = ?", (domain_label,)).fetchone()
    return int(row["id"]) if row else None


def _seed_all(conn: sqlite3.Connection) -> None:
    code_to_id = _seed_domains(conn)

    if SEED_PATH.is_file():
        seed = json.loads(SEED_PATH.read_text(encoding="utf-8"))
        for user in seed.get("users", []):
            conn.execute(
                "INSERT OR IGNORE INTO users (id, name, exam_date, hours_per_week, current_level) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    user["id"],
                    user["name"],
                    user.get("exam_date"),
                    user["hours_per_week"],
                    user["current_level"],
                ),
            )
        for result in seed.get("quiz_results", []):
            domain_id = _resolve_domain_id(conn, result["domain"], code_to_id)
            if domain_id is None:
                continue
            conn.execute(
                "INSERT INTO quiz_results (user_id, domain_id, score_percent, attempts) "
                "VALUES (?, ?, ?, ?)",
                (
                    result["user_id"],
                    domain_id,
                    result["score_percent"],
                    result.get("attempts", 1),
                ),
            )

    from app.services.flashcards import DEFAULT_FLASHCARDS
    from app.services.practice_questions import PRACTICE_QUESTIONS

    conn.execute("DELETE FROM flashcards")
    for card in DEFAULT_FLASHCARDS:
        domain_id = _resolve_domain_id(conn, card.domain, code_to_id)
        if domain_id is None:
            continue
        conn.execute(
            "INSERT INTO flashcards (domain_id, question, answer) VALUES (?, ?, ?)",
            (domain_id, card.question, card.answer),
        )

    conn.execute("DELETE FROM practice_questions")
    for question in PRACTICE_QUESTIONS:
        conn.execute(
            "INSERT INTO practice_questions ("
            "prompt, options_json, correct_option_index, explanation, "
            "distractor_rationales_json, references_json, domain, source, policy_note"
            ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                question.prompt,
                json.dumps(question.options),
                question.correct_option_index,
                question.explanation,
                json.dumps(question.distractor_rationales),
                json.dumps(question.references),
                question.domain,
                question.source,
                question.policy_note,
            ),
        )


def list_flashcards(conn: sqlite3.Connection, domain: str | None = None) -> list[dict[str, str]]:
    if domain:
        rows = conn.execute(
            """
            SELECT f.question, f.answer, d.title AS domain
            FROM flashcards f
            JOIN domains d ON f.domain_id = d.id
            WHERE d.title = ? OR d.code = ?
            ORDER BY f.id
            """,
            (domain, domain),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT f.question, f.answer, d.title AS domain
            FROM flashcards f
            JOIN domains d ON f.domain_id = d.id
            ORDER BY f.id
            """
        ).fetchall()
    return [{"question": r["question"], "answer": r["answer"], "domain": r["domain"]} for r in rows]


def list_practice_questions(conn: sqlite3.Connection, domain: str | None = None) -> list[dict[str, Any]]:
    if domain:
        rows = conn.execute(
            "SELECT * FROM practice_questions WHERE domain = ? OR domain LIKE ? ORDER BY id",
            (domain, f"%{domain}%"),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM practice_questions ORDER BY id").fetchall()

    results: list[dict[str, Any]] = []
    for row in rows:
        results.append(
            {
                "prompt": row["prompt"],
                "options": json.loads(row["options_json"]),
                "correct_option_index": row["correct_option_index"],
                "explanation": row["explanation"],
                "distractor_rationales": json.loads(row["distractor_rationales_json"]),
                "references": json.loads(row["references_json"]),
                "domain": row["domain"],
                "source": row["source"],
                "policy_note": row["policy_note"],
            }
        )
    return results


def list_domain_titles(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute("SELECT title FROM domains ORDER BY id").fetchall()
    return [r["title"] for r in rows]


def record_webhook_event(
    conn: sqlite3.Connection,
    *,
    delivery_id: str | None,
    event_type: str,
    action: str | None,
    installation_id: int | None,
    payload: dict[str, Any],
) -> None:
    conn.execute(
        "INSERT INTO github_webhook_events "
        "(delivery_id, event_type, action, installation_id, payload_json) "
        "VALUES (?, ?, ?, ?, ?)",
        (
            delivery_id,
            event_type,
            action,
            installation_id,
            json.dumps(payload),
        ),
    )


def upsert_installation(
    conn: sqlite3.Connection,
    *,
    installation_id: int,
    account_login: str | None,
    account_type: str | None,
) -> None:
    conn.execute(
        "INSERT INTO github_installations (installation_id, account_login, account_type) "
        "VALUES (?, ?, ?) "
        "ON CONFLICT(installation_id) DO UPDATE SET "
        "account_login = excluded.account_login, "
        "account_type = excluded.account_type, "
        "updated_at = CURRENT_TIMESTAMP",
        (installation_id, account_login, account_type),
    )


def list_recent_webhook_events(conn: sqlite3.Connection, limit: int = 20) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT id, delivery_id, event_type, action, installation_id, received_at "
        "FROM github_webhook_events ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    return [dict(r) for r in rows]


def list_installations(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT installation_id, account_login, account_type, updated_at "
        "FROM github_installations ORDER BY installation_id"
    ).fetchall()
    return [dict(r) for r in rows]
