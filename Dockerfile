# Dockerfile for testing the plugin in a containerized environment
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app/

# Make scripts executable
RUN chmod +x /app/setup.sh /app/test.sh /app/run.sh

# Install Python dependencies
RUN python -m pip install --upgrade pip && \
    pip install Pillow gradio

# Verify installations
RUN python -c "import PIL; print(f'Pillow {PIL.__version__} installed')" && \
    python -c "import gradio; print(f'Gradio {gradio.__version__} installed')"

# Default command: run the test suite
CMD ["/app/test.sh"]
