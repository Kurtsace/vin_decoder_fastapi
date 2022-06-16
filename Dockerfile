FROM python:3.9

WORKDIR /code 

EXPOSE 8000

COPY ./requirements.txt /code/requirements.txt

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--reload", "--port", "8000"]
