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
    wget \
    unzip \
    gnupg \
    && apt-get clean

# Install specific version of Google Chrome (114.0.5735.90)
RUN wget https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_114.0.5735.90-1_amd64.deb \
    && dpkg -i google-chrome-stable_114.0.5735.90-1_amd64.deb || apt-get -fy install \
    && rm google-chrome-stable_114.0.5735.90-1_amd64.deb

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install -r requirements.txt --no-cache-dir

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE ${PORT}

ARG SERVER_PORT=0.0.0.0:${PORT}

CMD [ "gunicorn", "-b", ${SERVER_PORT}, "main:app" ]