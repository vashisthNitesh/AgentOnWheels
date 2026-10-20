# ==============================================================================
# Stage 1: Build the Vue 3 frontend
# ==============================================================================
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

# Install dependencies first (leverage Docker layer caching)
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

# Copy frontend source and build production bundle
COPY frontend/ ./
RUN npm run build

# ==============================================================================
# Stage 2: Production Python container
# ==============================================================================
FROM python:3.12-slim AS runner

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Install minimal OS dependencies for Postgres client & health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY manage.py .
COPY config/ config/
COPY core/ core/
COPY templates/ templates/
COPY scripts/ scripts/

# Copy built frontend assets from stage 1
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist
COPY --from=frontend-builder /app/frontend/dist/index.html /app/templates/index.html

# Copy entrypoint script and make executable
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Collect static files into staticfiles directory served by WhiteNoise
RUN python manage.py collectstatic --noinput -v0

# Expose default port
EXPOSE 8000

# Run entrypoint script (runs migrations then starts gunicorn)
ENTRYPOINT ["/app/docker-entrypoint.sh"]
