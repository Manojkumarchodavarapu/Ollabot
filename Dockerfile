FROM ubuntu:22.04

# Basic setup
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    ca-certificates \
    python3 \
    python3-pip

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | bash

# Add ollama to PATH (if needed)
ENV PATH="/root/.ollama/bin:$PATH"

# Set up working directory
WORKDIR /app

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy the Streamlit app
COPY streamlit_app.py .

# Expose Streamlit port
EXPOSE 8501

# Expose Ollama port
EXPOSE 11434

# Run Ollama in the background & then run Streamlit
CMD ollama serve & \
    streamlit run streamlit_app.py --server.address=0.0.0.0
