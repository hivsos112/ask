# Use an official Python runtime as a parent image
# Use bullseye (Debian 11) for maximum compatibility with apt packages
FROM python:3.9-bullseye

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for OpenCV/CnOCR/OnnxRuntime
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && \
    pip list

# Copy the download script
COPY download_model.py /app/

# Download CnOCR model during build to avoid download at runtime
RUN python3 download_model.py && rm download_model.py

# Copy the current directory contents into the container at /app
COPY . /app

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=app.py

# Run app.py when the container launches using gunicorn
# Use shell form to expand PORT variable, defaulting to 5000 if not set
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5000} app:app"]
