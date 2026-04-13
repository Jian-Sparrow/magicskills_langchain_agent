FROM python:3.10-slim

LABEL maintainer="MagicSkills Docker Deployment"
LABEL version="2.0"
LABEL description="MagicSkills + LangGraph Agent with Intent Recognition"

WORKDIR /app

# Create non-root user for security
RUN useradd -m -u 1000 magicskills && \
    mkdir -p /app/workspace/skills/allskills \
    /app/workspace/logs \
    /app/workspace/data && \
    chown -R magicskills:magicskills /app

# Copy requirements first for better caching
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install magicskills directly from GitHub (no git client needed)
RUN pip install --no-cache-dir https://github.com/Narwhal-Lab/MagicSkills/archive/refs/heads/main.tar.gz

# Copy application code
COPY magicskills_api_v2_docker.py /app/magicskills_api_v2.py
COPY intent_recognition_demo.py /app/
COPY test_intent_llm.py /app/
COPY start.sh /app/

# Copy intent-recognition skill files
COPY workspace/skills/allskills/intent-recognition /app/workspace/skills/allskills/intent-recognition
COPY workspace/AGENTS.md /app/workspace/AGENTS.md

# Install skill dependencies
RUN pip install --no-cache-dir -r /app/workspace/skills/allskills/intent-recognition/requirements.txt

# Ensure symbolic link exists for skill execution
RUN cd /app/workspace/skills/allskills/intent-recognition && \
    test -e intent-recognition || ln -s intent_recognition.py intent-recognition && \
    chmod +x intent_recognition.py

# Set proper permissions
RUN chown -R magicskills:magicskills /app/workspace

# Switch to non-root user
USER magicskills

# Expose API port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Default command - start API and keep container running
CMD ["bash", "/app/start.sh"]