# ── Stage 1: Build React frontend ─────────────────────────────────────────────
FROM node:22-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# ── Stage 2: Combined image (Python + nginx) ───────────────────────────────────
FROM python:3.12-slim

# Install nginx and supervisor
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
WORKDIR /app/backend
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ ./

# Copy built frontend into nginx web root
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.railway.conf /etc/nginx/sites-enabled/default
RUN rm -f /etc/nginx/sites-enabled/default.bak

# Copy supervisor config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 80

# Railway injects $PORT — patch nginx to listen on it, then start supervisor
# (alembic migrations run via supervisord alongside nginx + uvicorn)
CMD ["/bin/sh", "-c", "\
  sed -i \"s/listen 80/listen ${PORT:-80}/g\" /etc/nginx/sites-enabled/default && \
  supervisord -c /etc/supervisor/conf.d/supervisord.conf"]
