FROM python:3.12

WORKDIR /code

COPY code/ /code/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --upgrade -r /code/requirements.txt
    
EXPOSE 1122
