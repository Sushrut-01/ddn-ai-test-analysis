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
RUN pip install --no-cache-dir -r requirements.txt && \
    pip uninstall -y pinecone-plugin-inference 2>/dev/null || true

# Copy application files
COPY *.py ./

# Copy agents directory (required for react_agent_service)
COPY agents/ ./agents/

# Copy tasks directory (required for celery tasks)
COPY tasks/ ./tasks/

# Copy retrieval directory (required for FusionRAG)
COPY retrieval/ ./retrieval/

# Copy workflows directory (required for Agentic Workflows API)
COPY workflows/ ./workflows/

# Set PYTHONPATH to include /app so all modules are found
ENV PYTHONPATH=/app

# Expose ports (individual services will use specific ports)
EXPOSE 5000 5004 5005 5006 5007 5008

# Default command (will be overridden by docker-compose)
CMD ["python", "langgraph_agent.py"]
