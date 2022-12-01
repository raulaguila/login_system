FROM python:3.11

WORKDIR /app

COPY . .

EXPOSE 7707

RUN /usr/local/bin/python -m pip install --upgrade pip

RUN pip install -r requirements.txt

# For production
CMD [ "gunicorn", "app.main:app", "--workers", "8", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:7707" ]
