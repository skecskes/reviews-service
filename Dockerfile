FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./src ./src

LABEL org.opencontainers.image.authors="Stefan Kecskes"
LABEL org.opencontainers.image.vendor="skecskes"
LABEL org.opencontainers.image.source="git@github.com:skecskes/reviews-service.git"
LABEL org.opencontainers.image.licenses="MIT"

ENV HTTP_SERVER_PORT=8000
ENV PGHOST="localhost"
ENV PGUSER="postgres"
ENV PGPASSWORD="postgres"
ENV PGPORT=5432
ENV PGDATABASE="reviews"

EXPOSE 8000
CMD ["sh", "-c", "uvicorn src.api.main:app --host 0.0.0.0 --port ${HTTP_SERVER_PORT}"]