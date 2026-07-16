# ==============================================================================
# SMART MONITOR PLATFORM - CENTRAL DASHBOARD ENGINE
# ==============================================================================
# Use an official lightweight Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Optimize python deployment layers and standard streams
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies required for compiling certain Python packages (like psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from the dashboard folder and install them
COPY dashboard/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy BOTH core and dashboard folders into the container to fix the import error
COPY core/ ./core/
COPY dashboard/ ./dashboard/

# Set the PYTHONPATH environment variable so Python knows where to look for imports
ENV PYTHONPATH=/app

# Expose port 5000 for the application to be accessible
EXPOSE 5000

# Command to run the Flask application from the dashboard folder using enterprise Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "dashboard.app:app"]