# Stage 1: Builder (Alpine-based)
FROM python:3.13-alpine AS builder

# Create the app directory
RUN mkdir /app

WORKDIR /app

# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 

# Alpine-specific: install build tools & pip
RUN apk add --no-cache gcc musl-dev libffi-dev build-base

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Final image
FROM python:3.13-alpine

# Non-root user
RUN useradd -m -r wordcard_user && \
   mkdir /app && \
   chown -R wordcard_user /app

# Copy deps from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
   
# Set the working directory
WORKDIR /app

# Copy application code
COPY --chown=wordcard_user:wordcard_user . .

# Static dir
RUN mkdir -p /app/staticfiles

# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 

# Make entrypoint executable
RUN chmod +x /app/entrypoint.prod.sh

USER wordcard_user

EXPOSE 8000

CMD ["/app/entrypoint.prod.sh"]