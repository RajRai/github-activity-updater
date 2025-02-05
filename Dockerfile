# Use the official Python image as a base
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main script and any other necessary files
COPY main.py ./

# Ensure git is installed
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Set environment variables (override in runtime)
ENV GITHUB_REPO=""
ENV GIT_USER_NAME=""
ENV GIT_USER_EMAIL=""
ENV GITHUB_TOKEN=""

# Run the script
CMD ["python", "main.py"]
