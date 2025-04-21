# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1 # Prevents python from writing .pyc files
ENV PYTHONUNBUFFERED 1 # Prevents python from buffering stdout and stderr

# Set the working directory in the container
WORKDIR /app

# Install system dependencies if needed (e.g., for certain libraries)
# RUN apt-get update && apt-get install -y --no-install-recommends some-package && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Use --no-cache-dir to reduce image size
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY src/ ./src/
COPY config/ ./config/
# Ensure data and logs directories exist (optional, can be mounted as volumes)
RUN mkdir -p data logs

# NOTE on Configuration:
# We copy the config directory, which might include .env.example.
# DO NOT commit your actual .env file with secrets into the Docker image.
# Provide secrets at runtime via environment variables or mounted volumes.
# Example: docker run -e NEWS_API_KEY=... -e LLM_API_KEY=... -v $(pwd)/config/.env:/app/config/.env my-agent-image
# Or better: Use Docker secrets or a configuration management system.

# Expose any ports if this were a web application (not needed for this agent)
# EXPOSE 8000

# Define the command to run the application
CMD ["python", "src/main.py"] 