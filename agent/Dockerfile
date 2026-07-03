# ==============================================================================
# SMART MONITOR PLATFORM - UNIFIED PRODUCTION AGENT CONTAINER
# ==============================================================================
FROM python:3.10-slim

# Set decentralized execution workspace boundaries
WORKDIR /app

# Optimize python layer deployment footprints
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y gcc python3-dev && rm -rf /var/lib/apt/lists/*

# Install core system dependencies using Docker container cache optimization
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the standardized lifecycle telemetry script and environment mappings
COPY agent.py .
# COPY .env .

# Trigger the non-blocking kernel infrastructure synchronization loop
CMD ["python", "agent.py"]