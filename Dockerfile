FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p data/raw data/output
CMD ["sh","-c","python src/generate_data.py && python src/pipeline.py"]
