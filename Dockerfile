FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    gcc \
    g++ \
    make \
    gnupg \
    nginx \
    supervisor \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY degree-recommendation-service/requirements.txt /app/degree-recommendation-service/requirements.txt
COPY career-service/requirements.txt /app/career-service/requirements.txt
COPY scholarship_and_loan_recommendation_service/requirements.txt /app/scholarship_and_loan_recommendation_service/requirements.txt
COPY budget_optimizer_service/requirements.txt /app/budget_optimizer_service/requirements.txt

RUN pip install --no-cache-dir -r /app/degree-recommendation-service/requirements.txt \
    && pip install --no-cache-dir -r /app/career-service/requirements.txt \
    && pip install --no-cache-dir -r /app/scholarship_and_loan_recommendation_service/requirements.txt \
    && pip install --no-cache-dir -r /app/budget_optimizer_service/requirements.txt

COPY backend/package*.json /app/backend/
RUN cd /app/backend && npm ci --omit=dev

COPY backend /app/backend
COPY degree-recommendation-service /app/degree-recommendation-service
COPY budget_optimizer_service /app/budget_optimizer_service
COPY career-service /app/career-service
COPY scholarship_and_loan_recommendation_service /app/scholarship_and_loan_recommendation_service
COPY deploy/hf /app/deploy/hf

RUN rm -f /etc/nginx/sites-enabled/default
COPY deploy/hf/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 7860

CMD ["/usr/bin/supervisord", "-c", "/app/deploy/hf/supervisord.conf"]

