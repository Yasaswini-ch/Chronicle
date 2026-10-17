# ---- Stage 1: build the React frontend ----
FROM node:22-slim AS frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ---- Stage 2: Python runtime ----
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    CHRONICLE_ROOT=/app \
    CHRONICLE_HOST=0.0.0.0 \
    CHRONICLE_PORT=8000 \
    HF_HOME=/app/.cache/huggingface

WORKDIR /app
RUN useradd --create-home --uid 1000 chronicle

COPY pyproject.toml README.md ./
COPY src/ ./src/
RUN pip install ".[ml]" && python -m spacy download en_core_web_sm \
    && python -m nltk.downloader -d /usr/share/nltk_data punkt punkt_tab stopwords wordnet averaged_perceptron_tagger

COPY data/ ./data/
COPY --from=frontend /app/frontend/dist ./frontend/dist

# Pre-download the SBERT model so the container does not need the network at start-up
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')" \
    && chown -R chronicle:chronicle /app

USER chronicle
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/api/ready').status==200 else 1)"

CMD ["chronicle-api"]
