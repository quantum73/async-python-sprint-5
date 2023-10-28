FROM python:3.11-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY . /app

RUN apk add --update --no-cache --virtual .tmp-build-deps gcc libc-dev linux-headers postgresql-dev  \
    && apk add libffi-dev
RUN pip install --upgrade --no-cache-dir pip && pip install --no-cache-dir -r ./requirements.txt