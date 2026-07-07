from app.schemas import PracticeQuestion

COMPLIANCE_NOTE = (
    "These are original skills-practice questions aligned to Cisco 200-901 DEVASC "
    "topics (APIs, Python, security, Cisco platforms, and automation). They are not "
    "official live exam questions."
)


PRACTICE_QUESTIONS = [
    PracticeQuestion(
        prompt=(
            "You need to collect interface counters from multiple routers every 5 minutes. "
            "Which automation approach is most scalable?"
        ),
        options=[
            "SSH manually into each router and copy/paste output",
            "Automate polling via API/NETCONF and store structured results",
            "Use a one-time Python script and stop collecting after first run",
            "Disable telemetry and rely only on syslog",
        ],
        correct_option_index=1,
        explanation=(
            "Automated, scheduled polling with structured parsing scales better and supports "
            "trending/alerts."
        ),
        distractor_rationales=[
            "Manual SSH does not scale and creates inconsistent, non-repeatable data capture.",
            "Correct: API/NETCONF polling with structured output supports "
            "repeatable automation workflows.",
            "A one-time script cannot provide continuous monitoring or trend analysis.",
            "Disabling telemetry removes observability and weakens incident response.",
        ],
        references=[
            "Integration Blueprint: Training Engine → Analytics uses event-driven "
            "patterns for scale.",
            "Architecture Map: Core Services emphasize automation orchestration "
            "and telemetry workflows.",
        ],
        domain="DEVASC 5.0 Infrastructure and Automation",
        source="Original",
        policy_note=COMPLIANCE_NOTE,
    ),
    PracticeQuestion(
        prompt=(
            "In a DEVASC-style CI workflow for Python automation scripts, what is the best "
            "reason to require pull requests?"
        ),
        options=[
            "To prevent all collaboration",
            "To enforce peer review and CI checks before merging",
            "To avoid using version control history",
            "To replace testing entirely",
        ],
        correct_option_index=1,
        explanation="PRs allow code review, automated tests, and safer change control.",
        distractor_rationales=[
            "Blocking collaboration slows delivery and reduces learning through review.",
            "Correct: PRs gate merges behind review and CI, reducing production regressions.",
            "Skipping history removes traceability and rollback confidence.",
            "Testing is still required; PR process complements it, not replaces it.",
        ],
        references=[
            "Launch Plan: phased delivery depends on controlled releases and validation gates.",
            "Risk Matrix: change-risk mitigation favors review and quality controls "
            "before release.",
        ],
        domain="DEVASC 1.0 Software Development and Design",
        source="Original",
        policy_note=COMPLIANCE_NOTE,
    ),
    PracticeQuestion(
        prompt=(
            "A REST API returns JSON for device inventory. What is the safest first step in a "
            "Python automation pipeline before using values in templates?"
        ),
        options=[
            "Assume all keys exist and render immediately",
            "Validate schema and handle missing/null fields",
            "Convert JSON to plain text manually",
            "Disable API authentication",
        ],
        correct_option_index=1,
        explanation="Validation prevents bad automation output and runtime failures.",
        distractor_rationales=[
            "Assuming keys exist causes brittle templates and failed automation runs.",
            "Correct: schema validation catches missing fields and keeps pipeline outputs safe.",
            "Manual text conversion discards structure and increases processing errors.",
            "Disabling authentication introduces major security and compliance risk.",
        ],
        references=[
            "Integration Blueprint: JSON payload handling and auth controls are "
            "explicit interface requirements.",
            "Risk Matrix: security and data-quality risks increase when "
            "validation/auth are skipped.",
        ],
        domain="DEVASC 2.0 Understanding and Using APIs",
        source="Original",
        policy_note=COMPLIANCE_NOTE,
    ),
    PracticeQuestion(
        prompt=(
            "Your automation script must update 200 managed devices without overloading "
            "controller resources. What is the best execution strategy?"
        ),
        options=[
            "Send all requests at once with no delay",
            "Batch updates with bounded concurrency and retry/backoff logic",
            "Disable logging to improve speed",
            "Run updates manually one device at a time forever",
        ],
        correct_option_index=1,
        explanation=(
            "Bounded concurrency with retries improves throughput while reducing platform stress "
            "and transient-failure impact."
        ),
        distractor_rationales=[
            "Unbounded bursts can trigger throttling and instability.",
            "Correct: controlled parallelism is a standard automation reliability pattern.",
            "Removing logs harms observability and rollback diagnostics.",
            "Manual-only workflows do not scale for production operations.",
        ],
        references=[
            "Integration Blueprint: latency and pattern constraints imply controlled request flow.",
            "Risk Matrix: operational risk increases when change execution is unmanaged.",
        ],
        domain="DEVASC 5.0 Infrastructure and Automation",
        source="Original",
        policy_note=COMPLIANCE_NOTE,
    ),
    PracticeQuestion(
        prompt=(
            "In a GitHub Actions pipeline for Python automation scripts, which sequence is most "
            "appropriate before merge?"
        ),
        options=[
            "Skip tests and merge if code looks clean",
            "Run lint + unit tests + sample payload validation, then require PR approval",
            "Merge directly to main then test in production",
            "Disable branch protection to speed delivery",
        ],
        correct_option_index=1,
        explanation="Pre-merge quality gates reduce defects and protect automation reliability.",
        distractor_rationales=[
            "Visual review alone misses behavioral regressions.",
            "Correct: layered validation and approval are core CI/CD safeguards.",
            "Production-first testing creates avoidable incidents.",
            "Removing protections undermines release governance.",
        ],
        references=[
            "Launch Plan: staged quality gates are required for stable rollout.",
            "Risk Matrix: weak change controls are a key delivery risk.",
        ],
        domain="DEVASC 1.0 Software Development and Design",
        source="Original",
        policy_note=COMPLIANCE_NOTE,
    ),
    PracticeQuestion(
        prompt=(
            "A Python script consumes API responses with optional fields. Which coding pattern "
            "best prevents runtime key errors?"
        ),
        options=[
            "Use direct dictionary indexing everywhere",
            "Use safe access patterns (`get`) with schema validation/default handling",
            "Convert JSON to CSV before parsing",
            "Ignore missing fields and continue silently",
        ],
        correct_option_index=1,
        explanation=(
            "Safe access and schema-aware defaults protect the pipeline from malformed or partial "
            "payloads."
        ),
        distractor_rationales=[
            "Direct indexing fails fast when keys are missing.",
            "Correct: safe access plus validation improves robustness.",
            "Format conversion does not solve missing-field semantics.",
            "Silent failures hide data quality issues.",
        ],
        references=[
            "Integration Blueprint: JSON contract handling is critical at service boundaries.",
            "Risk Matrix: hidden data defects create downstream automation incidents.",
        ],
        domain="DEVASC 2.0 Understanding and Using APIs",
        source="Original",
        policy_note=COMPLIANCE_NOTE,
    ),
    PracticeQuestion(
        prompt=(
            "You need to rollback a failed automation deployment quickly. What repository "
            "practice helps most?"
        ),
        options=[
            "Keep one giant commit for the whole quarter",
            "Use small, descriptive commits and tagged releases",
            "Delete commit history monthly",
            "Store scripts outside version control",
        ],
        correct_option_index=1,
        explanation=(
            "Granular commit history and release tags make rollback targeted, fast, and auditable."
        ),
        distractor_rationales=[
            "Large commits make rollback risky and imprecise.",
            "Correct: clear history and tagging support controlled recovery.",
            "History deletion breaks traceability and governance.",
            "External script storage removes collaboration and safety controls.",
        ],
        references=[
            "Launch Plan: release discipline depends on traceable version control artifacts.",
            "Risk Matrix: recovery speed is tied to change-management quality.",
        ],
        domain="DEVASC 4.0 Application Deployment and Security",
        source="Original",
        policy_note=COMPLIANCE_NOTE,
    ),
    PracticeQuestion(
        prompt=(
            "When generating infrastructure configs from structured data, what should be "
            "validated before rendering final output?"
        ),
        options=[
            "Only that the template file exists",
            "Input schema, required variables, and allowed value ranges",
            "Whether the terminal font is monospaced",
            "That all hostnames are less than 3 characters",
        ],
        correct_option_index=1,
        explanation=(
            "Input validation prevents invalid configurations and reduces failed deployment events."
        ),
        distractor_rationales=[
            "Template existence alone does not validate data correctness.",
            "Correct: schema + constraints ensure safe config generation.",
            "Font choices are unrelated to automation correctness.",
            "Arbitrary hostname limits are not meaningful validation.",
        ],
        references=[
            "Architecture Map: automation services rely on trustworthy structured inputs.",
            "Risk Matrix: misconfiguration risk drops with strong validation controls.",
        ],
        domain="DEVASC 3.0 Cisco Platforms and Development",
        source="Original",
        policy_note=COMPLIANCE_NOTE,
    ),
]


def get_practice_questions(domain: str | None = None) -> list[PracticeQuestion]:
    try:
        from app.db import get_connection, list_practice_questions

        with get_connection() as conn:
            rows = list_practice_questions(conn, domain)
        if rows:
            return [PracticeQuestion(**row) for row in rows]
    except Exception:
        pass
    if not domain:
        return PRACTICE_QUESTIONS
    return [q for q in PRACTICE_QUESTIONS if q.domain.lower() == domain.lower()]
