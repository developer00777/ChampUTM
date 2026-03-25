FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download GeoLite2-City database (requires free MaxMind license key)
ARG MAXMIND_LICENSE_KEY=""
RUN mkdir -p /app/geoip && \
    if [ -n "$MAXMIND_LICENSE_KEY" ]; then \
        wget -q "https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-City&license_key=${MAXMIND_LICENSE_KEY}&suffix=tar.gz" \
             -O /tmp/geolite2.tar.gz && \
        tar -xzf /tmp/geolite2.tar.gz -C /tmp && \
        mv /tmp/GeoLite2-City_*/GeoLite2-City.mmdb /app/geoip/ && \
        rm -rf /tmp/geolite2.tar.gz /tmp/GeoLite2-City_* && \
        echo "GeoLite2-City database downloaded successfully"; \
    else \
        echo "MAXMIND_LICENSE_KEY not set — geo lookups will be disabled"; \
    fi

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run migrations then start the server
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
