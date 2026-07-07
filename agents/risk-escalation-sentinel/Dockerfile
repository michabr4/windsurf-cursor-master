FROM python:3.11-slim

WORKDIR /app

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appgroup . .

USER appuser

ENV LOG_LEVEL=INFO \
    LOOKBACK_DAYS=7 \
    DRY_RUN=false

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import config; config.get_settings()" || exit 1

CMD ["python", "main.py"]
