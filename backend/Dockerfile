FROM python:3.11-slim

WORKDIR /code

# Устанавливаем зависимости
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Копируем остальной код
COPY ./app /code/app

# Запускаем FastAPI с hot-reload для удобной разработки
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
