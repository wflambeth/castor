FROM python:3.11-slim-bookworm

WORKDIR /app

COPY requirements.txt /tmp/requirements.txt

RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /root/.cache/

COPY . /app/

ENV DJANGO_SETTINGS_MODULE=castor.settings

RUN python manage.py collectstatic --noinput

EXPOSE 8000 5432

CMD ["gunicorn", "--bind", ":8000", "--workers", "2", "castor.wsgi"]
