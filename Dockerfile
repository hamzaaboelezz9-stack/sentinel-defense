# syntax=docker/dockerfile:1
# Release image uses the validated prebuilt frontend included in the source archive.
FROM python:3.12-slim
WORKDIR /app
COPY backend/ backend/
COPY frontend/dist/ frontend/dist/
RUN --mount=type=secret,id=proxy_ca,required=false \
    if [ -f /run/secrets/proxy_ca ]; then PIP_CERT=/run/secrets/proxy_ca pip install --no-cache-dir -r backend/requirements.lock; else pip install --no-cache-dir -r backend/requirements.lock; fi \
    && useradd -m sentinel && mkdir /data && chown -R sentinel:sentinel /app /data
USER sentinel
ENV DATABASE_URL=sqlite:////data/sentinel.db
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/ready')"
CMD ["python","-m","uvicorn","backend.app.main:app","--host","0.0.0.0","--port","8000"]
