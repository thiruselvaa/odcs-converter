FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create app user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update     && apt-get install -y --no-install-recommends         gcc         libc6-dev     && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY pyproject.toml .
COPY README.md .

# Install the package
RUN pip install -e .

# Change to app user
RUN chown -R appuser:appuser /app
USER appuser

# Create data directory for mounted volumes
RUN mkdir -p /app/data

# Set the default command
ENTRYPOINT ["odcs-converter"]
CMD ["--help"]
