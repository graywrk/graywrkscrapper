FROM python:3-bullseye

WORKDIR /app

COPY requirements.txt ./

COPY main.py ./

COPY *.session ./

COPY .env ./

RUN pip install -r requirements.txt

CMD ["python", "/app/main.py" ]