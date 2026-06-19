# ==============================================================================
# SMART MONITOR PLATFORM - UNIFIED AGENT CONTAINER
# ==============================================================================
FROM python:3.10-slim

# Set system environment boundaries
WORKDIR /app

# Optimize python deployment layers
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV AGENT_NAME=docker-default-agent

# Install core dependencies using Docker cache optimization
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the unified execution script and its dependent metrics engine
COPY agent.py .
# COPY metrics.py .

# Trigger the non-blocking monitoring loop
CMD ["python", "agent.py"]