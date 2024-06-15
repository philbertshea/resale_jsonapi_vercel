ARG PORT=443
FROM cypress/browsers:latest

# Install Python
RUN apt-get update && apt-get install -y python3 python3-pip python3-dev build-essential libssl-dev libffi-dev

# Check Python user base
RUN echo $(python3 -m site --user-base)

# Copy requirements file
COPY requirements.txt .

# Set environment variable for PATH
ENV PATH /home/root/.local/bin:${PATH}

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir --verbose

# Copy the rest of the application code
COPY . .

# Specify the command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "${PORT}"]