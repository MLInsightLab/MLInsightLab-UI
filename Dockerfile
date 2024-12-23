FROM python:3.12

# Update software
RUN apt update && apt upgrade -y && apt autoremove -y

# Change working directory
WORKDIR /code

# Copy necessary files
COPY code/ /code/

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --upgrade -r /code/requirements.txt
    
# Expose necessary port
EXPOSE 1122
