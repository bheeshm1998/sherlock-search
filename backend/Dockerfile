# Use an official Python runtime as a parent image
FROM python:3.12-slim AS builder

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Use a minimal final image
FROM python:3.12-slim

WORKDIR /app

# Copy installed dependencies from the builder stage
COPY --from=builder /install /usr/local

# Copy the application code
COPY . .

# Expose port 80
EXPOSE 80

# Run the FastAPI application with Gunicorn and Uvicorn workers
CMD ["gunicorn", "--bind", "0.0.0.0:80", "-k", "uvicorn.workers.UvicornWorker", "app.main:app"]
