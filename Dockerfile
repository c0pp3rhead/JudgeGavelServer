# Use official, stable Python 3.11 image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy your requirement files
COPY requirements.txt .

# Install dependencies directly to the global system (no .venv needed)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the actual code
COPY main.py .

# Force uvicorn to run on the dynamic port Render assigns
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]