#!/bin/sh

while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      sleep 0.1
done

alembic upgrade head
python main.py

#exec "$@"