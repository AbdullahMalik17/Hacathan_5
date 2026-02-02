# Task T102: Backend Dockerfile with multi-stage build
# Customer Success Digital FTE - Backend API & Workers

# Stage 1: Build dependencies
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Copy requirements
COPY requirements.txt .

# Install dependencies into venv
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime image
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 appuser

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appuser /app/venv /app/venv

# Copy application code
COPY --chown=appuser:appuser src/ ./src/

# Switch to non-root user
USER appuser

# Enable venv
ENV PATH="/app/venv/bin:$PATH"

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command (API server)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Alternative command for workers (override in deployment):
# CMD ["python", "-m", "src.workers.message_processor"]
