# Stage 1: Build React frontend
FROM node:26-alpine AS frontend-builder

WORKDIR /frontend

# Copy package files first for better layer caching
COPY cst-frontend/package*.json ./
RUN npm ci

# Copy source and build
COPY cst-frontend/ ./
RUN npm run build

# Stage 2: Python backend with FastAPI
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies for PySide6 (if needed in production)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libxkbcommon0 \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code (excluding files in .dockerignore)
COPY . .

# Copy built React frontend from stage 1
COPY --from=frontend-builder /frontend/dist ./cst-frontend/dist

# Expose port for FastAPI
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health')" || exit 1

# Run FastAPI with uvicorn
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
