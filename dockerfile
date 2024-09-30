# Use the official Python image as a base
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1  
ENV PYTHONUNBUFFERED=1         

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 80 (for the host) instead of 8000
EXPOSE 80

# Command to run the application on port 80
CMD ["uvicorn", "trashapi.asgi:application", "--host", "0.0.0.0", "--port", "80", "--log-level", "debug"]
