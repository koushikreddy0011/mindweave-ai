# Multi-stage production build for MindWeave AI Backend
FROM python:3.11-slim AS builder
WORKDIR /app
# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final Runtime Image
FROM python:3.11-slim AS runner
WORKDIR /app
# Install runtime dependencies including curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*
# Create unprivileged application user
RUN groupadd -g 10001 mindweave && \
    useradd -u 10001 -g mindweave -m -s /bin/bash mindweave
# Copy installed wheels from builder
COPY --from=builder /root/.local /home/mindweave/.local
ENV PATH=/home/mindweave/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
# Copy application source code
COPY --chown=mindweave:mindweave alembic.ini .
COPY --chown=mindweave:mindweave alembic ./alembic
COPY --chown=mindweave:mindweave app ./app
COPY --chown=mindweave:mindweave entrypoint.sh .
# Ensure entrypoint is executable
RUN chmod +x entrypoint.sh
USER mindweave
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health/ready || exit 1
ENTRYPOINT ["./entrypoint.sh"]
