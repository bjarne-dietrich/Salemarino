# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app
RUN mkdir /app/templates
RUN mkdir /app/static

# Copy the current directory contents into the container at /app
COPY app.py /app
COPY templates/* /app/templates
COPY static /app/static
COPY requirements.txt /app
# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that Flask is running on
EXPOSE 5000

# Define the command to run your Flask application
CMD ["python", "app.py"]