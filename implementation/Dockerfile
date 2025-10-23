FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY *.py ./

# Expose ports (individual services will use specific ports)
EXPOSE 5000 5004 5005 5006 5007 5008

# Default command (will be overridden by docker-compose)
CMD ["python", "langgraph_agent.py"]
