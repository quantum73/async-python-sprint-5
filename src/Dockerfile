FROM python:3.11-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY . /app

RUN apk add --update --no-cache gcc libc-dev linux-headers postgresql-dev netcat-openbsd && apk add libffi-dev
RUN pip install --upgrade --no-cache-dir pip && pip install --no-cache-dir -r ./requirements.txt

RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["entrypoint.sh"]