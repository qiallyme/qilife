# Use a slim Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /usr/src/app

# Install system deps (if any), then Python deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy in your app code
COPY . .

# Expose Streamlit’s default port
EXPOSE 8501

# Launch Streamlit in headless mode
CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
