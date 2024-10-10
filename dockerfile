# Stage 1: Build
FROM python:3.9-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1  
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install build tools and dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get remove --purge -y gcc g++ \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Runtime
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1  
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy installed packages from the builder stage
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

# Copy the rest of the application code
COPY . .

# Expose port 80
EXPOSE 80

# Command to run the application on port 80
CMD ["uvicorn", "trashapi.asgi:application", "--host", "0.0.0.0", "--port", "8000", "--log-level", "debug"]
