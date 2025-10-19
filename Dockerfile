FROM python:3.11-slim

WORKDIR /app

RUN groupadd -r appuser && useradd -r -g appuser appuser

RUN mkdir -p /app/logs && chown -R appuser:appuser /app/logs

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY web_app.py .

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

CMD ["python", "web_app.py"]