FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install worker dependencies
COPY services/worker/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared config/logging and worker code
COPY shared ./shared
COPY services/worker ./services/worker

# Make top-level packages importable
ENV PYTHONPATH=/app

CMD ["python", "services/worker/main.py"]
