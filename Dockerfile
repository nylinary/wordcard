# Stage 1: Builder (Alpine-based)
FROM python:3.13-alpine AS builder

WORKDIR /app

# Alpine-specific: install build tools & pip
RUN apk add --no-cache gcc musl-dev libffi-dev build-base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Final image
FROM python:3.13-alpine

# Non-root user
RUN addgroup -S wordgroup && adduser -S wordcard_user -G wordgroup && mkdir -p /app && chown -R wordcard_user:wordgroup /app

# Copy deps from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

WORKDIR /app

# Copy app code
COPY --chown=wordcard_user:wordgroup . .

USER wordcard_user

# Static dir
RUN mkdir -p /app/staticfiles

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

# Make entrypoint executable
RUN chmod +x /app/entrypoint.prod.sh

CMD ["/app/entrypoint.prod.sh"]