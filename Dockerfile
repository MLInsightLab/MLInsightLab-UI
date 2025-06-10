FROM python:3.12-slim

# Update software
RUN apt update && apt upgrade -y && apt autoremove -y && apt install build-essential -y

# Change working directory
WORKDIR /code

# Copy necessary files
COPY code/ /code/

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip uv && \
    uv pip install --system --no-cache-dir --upgrade -r /code/requirements.txt
    
# Expose necessary port
EXPOSE 1122
