FROM python:3.13-slim

WORKDIR /.

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make entrypoint executable
RUN chmod +x docker-entrypoint.sh

# Create directory for ChromaDB
RUN mkdir -p chroma_db

# Initialize the vector store with products (if needed)
RUN python init_agent.py || true

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "run.py"]