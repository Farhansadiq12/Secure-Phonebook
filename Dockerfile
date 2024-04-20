# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8001 to allow external access to the FastAPI application
EXPOSE 8001

# Command to run the FastAPI application with hot-reloading when the container starts
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081", "--reload"]





