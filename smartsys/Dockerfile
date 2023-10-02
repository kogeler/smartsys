FROM python:3.11-alpine

ADD requirements.txt /requirements.txt

RUN apk add --no-cache postgresql-dev gcc musl-dev libffi-dev
RUN pip3 install --no-cache-dir -r /requirements.txt

ADD src /app
WORKDIR /app

ENTRYPOINT ["python3"]
