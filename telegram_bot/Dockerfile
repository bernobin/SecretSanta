
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY telegram_bot/ /app/

RUN python -m pip install --no-cache-dir .

CMD ["python", "-m", "secret_santa_bot"]
