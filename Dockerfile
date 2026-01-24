FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app ./app

# Expose port 10000  
EXPOSE 10000

# Start command -
# Using --timeout-keep-alive to prevent timeouts on heavy operations
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000", "--timeout-keep-alive", "120"]
