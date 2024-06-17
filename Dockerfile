# Use a Python base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    && apt-get clean

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install -r requirements.txt --no-cache-dir

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]