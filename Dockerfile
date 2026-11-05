FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["sh", "-c", "uvicorn backend.main:app --host 127.0.0.1 --port 8000 & streamlit run app.py --server.address 0.0.0.0 --server.port ${PORT:-8501}"]