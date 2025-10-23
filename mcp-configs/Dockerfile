FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from parent directory
COPY ../implementation/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy MCP server files
COPY *.py ./

# Expose ports
EXPOSE 5001 5002 5003

# Default command (will be overridden by docker-compose)
CMD ["python", "mcp_mongodb_server.py"]
