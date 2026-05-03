# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Run the application using Uvicorn
# --host 0.0.0.0 is required to allow external connections to the container
CMD ["uvicorn", "src.presentation.app:app", "--host", "0.0.0.0", "--port", "8000"]
