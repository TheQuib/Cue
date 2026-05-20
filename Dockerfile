FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    cec-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

ENV CONFIG_PATH=/app/config.yml

EXPOSE 5000

CMD ["python", "app.py"]
