FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libmagic1 \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python requirements
COPY requirements/base.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY backend/ /app/backend/

ENV PYTHONPATH=/app/backend

EXPOSE 8000

CMD ["python", "backend/main.py"]
