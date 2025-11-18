FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY input.py fixed_plugin.py test_plugin.py ./
COPY modules/ ./modules/
COPY setup.sh run.sh test.sh ./

# Make scripts executable
RUN chmod +x setup.sh run.sh test.sh

# Run setup (creates venv and installs dependencies)
RUN ./setup.sh

# Activate venv and run tests
CMD ["bash", "-c", "source venv/bin/activate && ./test.sh"]

