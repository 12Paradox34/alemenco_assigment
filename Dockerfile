# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install PostgreSQL client and netcat
RUN apt-get update && apt-get install -y postgresql-client netcat-openbsd


# Set the working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy app code
COPY . /app/

# Make entrypoint script executable
RUN chmod +x /app/entry_point.sh

# Set entrypoint
ENTRYPOINT ["/app/entry_point.sh"]

