# Use a Python base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies and Chrome dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libu2f-udev \
    libvulkan1 \
    xvfb \
    xauth \
    --no-install-recommends \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

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

# Copy the requirements file into the container
COPY requirements.txt .

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install -r requirements.txt --no-cache-dir

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application using the PORT environment variable
CMD ["sh", "-c", "xvfb-run --server-args='-screen 0 1280x1024x24' gunicorn -w 4 -b 0.0.0.0:${PORT} main:app"]
