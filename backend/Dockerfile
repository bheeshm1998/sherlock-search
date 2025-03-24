# Use an official Python runtime as a parent image
FROM python:3.11-slim AS builder

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
FROM python:3.11-slim
WORKDIR /app
# Copy the current directory contents into the container at /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable


# Run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]