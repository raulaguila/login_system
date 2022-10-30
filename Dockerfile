FROM python:3.10.8

WORKDIR /app

COPY . .

EXPOSE 7707

RUN /usr/local/bin/python -m pip install --upgrade pip

RUN pip install -r requirements.txt

# For production
CMD [ "gunicorn", "app.main:app", "--workers", "8", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:7707" ]

# For development
# CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7707", "--reload" ]
