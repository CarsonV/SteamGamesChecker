FROM python:3.9.12-slim-bullseye

WORKDIR /usr/src/app

RUN apt-get update \
    && apt-get -y install libpq-dev gcc

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./main.py" ]