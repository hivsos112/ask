# Use an official Python runtime as a parent image
# Use full python image to ensure all standard libraries are present
FROM python:3.9

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
# Force uninstallation of opencv-python (standard) to avoid conflicts with headless
RUN pip install --no-cache-dir -r requirements.txt && \
    pip uninstall -y opencv-python || true && \
    pip install opencv-python-headless

# Download CnOCR model during build to avoid download at runtime
# Print traceback if it fails
RUN python3 -c "import traceback, sys; \
try: \
    print('Checking imports...', flush=True); \
    import cv2; \
    print('cv2 imported successfully', flush=True); \
    import onnxruntime; \
    print('onnxruntime imported successfully', flush=True); \
    from cnocr import CnOcr; \
    print('Downloading CnOCR model...', flush=True); \
    CnOcr(); \
    print('Model downloaded successfully.', flush=True); \
except Exception: \
    traceback.print_exc(); \
    exit(1)"

# Copy the current directory contents into the container at /app
COPY . /app

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=app.py

# Run app.py when the container launches using gunicorn
# Use shell form to expand PORT variable, defaulting to 5000 if not set
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5000} app:app"]
