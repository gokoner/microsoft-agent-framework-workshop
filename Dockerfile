# Microsoft Agent Framework Workshop - Docker Image
# Build: docker build -t agent-workshop .
# Run: docker run -p 8888:8888 -v $(pwd):/workspace agent-workshop

FROM python:3.11-slim

# Set working directory
WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-dev.txt

# Copy workshop content
COPY . .

# Expose Jupyter port
EXPOSE 8888

# Set environment variable for Jupyter
ENV JUPYTER_ENABLE_LAB=yes

# Default command: Start JupyterLab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
