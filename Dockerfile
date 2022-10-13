FROM python:3.10.6

WORKDIR /app

COPY . .

EXPOSE 7707

RUN /usr/local/bin/python -m pip install --upgrade pip

RUN pip install -r requirements.txt

# CMD [ "gunicorn", "app.main:app", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:7707" ]

CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7707", "--reload" ]
