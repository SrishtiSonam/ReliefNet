FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies before copying source (better layer caching)
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
 && pip install --no-cache-dir \
      gymnasium \
      "stable-baselines3[extra]" \
      shap \
      torch --index-url https://download.pytorch.org/whl/cpu

# Copy source — layout must match what main.py expects:
#   /app/backend/app/main.py  →  parents[2] = /app  →  ml_services importable
COPY backend/  ./backend/
COPY ml_services/ ./ml_services/
COPY data/     ./data/

WORKDIR /app/backend

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
