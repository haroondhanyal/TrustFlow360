FROM python:3.12-slim
WORKDIR /service
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY apps/api/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY apps/api/ ./
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
