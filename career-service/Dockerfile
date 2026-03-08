# Career Service Dockerfile (FastAPI/Python)
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and ML artifacts
COPY . .

# Expose port
EXPOSE 5004

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5004/health')"

# Start the application
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5004"]
