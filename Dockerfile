# Use the official Python 3.12 image as the base image
FROM python:3.12

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file to the working directory
COPY requirements.txt .
COPY credentials.json .
COPY seen.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Set the entry point command to run your Python program
CMD ["python", "main.py"]