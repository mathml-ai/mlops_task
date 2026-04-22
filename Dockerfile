FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "run.py", \
     "--input", "data.csv", \
     "--config", "config.yaml", \
     "--output", "metrics.json", \
     "--log-file", "run.log"]