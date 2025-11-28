# Day 04 - Cardano Blockchain Transparency Pipeline
# Docker container for extracting and loading on-chain metrics

FROM python:3.11-slim

LABEL maintainer="Day 04 - Cardano Transparency Pipeline"
LABEL description="Extracts Cardano blockchain transparency metrics via Blockfrost API"

# Set working directory
WORKDIR /app

# Install system dependencies (if needed for BigQuery)
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY day04_requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r day04_requirements.txt

# Copy all day04 Python files
COPY day04_*.py ./

# Create data directories
RUN mkdir -p data/raw data/processed

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Default command: Extract data
# To load to BigQuery, override with: docker-compose run app python day04_DATA_load_bigquery.py
CMD ["python", "day04_DATA_extract_blockfrost.py"]
