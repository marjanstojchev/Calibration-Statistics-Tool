# Use official Python image as base
FROM python:3.13-slim

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . .

# Set default command
CMD ["python", "main.py"]
