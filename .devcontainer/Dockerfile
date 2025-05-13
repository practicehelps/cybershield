# app/Dockerfile

FROM python:3.13-slim

WORKDIR /usr/src/app
COPY app.py ./
COPY mcp_server ./mcp_server

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/practicehelps/cybershield.git .

RUN pip3 install -r requirements.txt

EXPOSE 8501