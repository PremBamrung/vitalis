# Use the official Python base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY ./app ./app
COPY ./data ./data
COPY ./db ./db

# Specify the command to run the Streamlit app
CMD ["streamlit", "run", "app/main.py"]
