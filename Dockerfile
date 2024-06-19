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
    curl \
    xvfb \
    && apt-get clean

# Download and install specific version of Google Chrome (126.0.6478.61)
RUN wget https://storage.googleapis.com/chrome-for-testing-public/126.0.6478.61/linux64/chrome-linux64.zip \
    && unzip chrome-linux64.zip -d /opt/ \
    && rm chrome-linux64.zip \
    && ln -s /opt/chrome-linux64/chrome /usr/local/bin/google-chrome

# Download and install specific version of ChromeDriver (126.0.6478.61)
RUN wget https://storage.googleapis.com/chrome-for-testing-public/126.0.6478.61/linux64/chromedriver-linux64.zip \
    && unzip chromedriver-linux64.zip -d /opt/ \
    && rm chromedriver-linux64.zip \
    && ln -s /opt/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver

# Ensure the chromedriver binary is executable
RUN chmod +x /usr/local/bin/chromedriver

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install -r requirements.txt --no-cache-dir

# Copy the rest of the application code
COPY . .

ARG port=5000

ENV port=$PORT
# Expose the port the app runs on
EXPOSE $port

ARG SERVER_PORT=0.0.0.0:$port

CMD ["gunicorn", "-w", "4", "-b", ${SERVER_PORT}, "main:app" ]