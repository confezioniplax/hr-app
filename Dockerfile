FROM python:3.10-slim

WORKDIR /code
COPY ./requirements.txt /code/requirements.txt

RUN apt-get update && \
    apt-get install -y gcc libmariadb-dev-compat libmariadb-dev pkg-config

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

ENV API_MYSQL_HOSTNAME=host.docker.internal
ENV API_MYSQL_PORT=3307
ENV API_MYSQL_USERNAME=root
ENV API_MYSQL_PASSWORD=root
ENV SECRET_KEY_JWT=b9aeb1ac75e5a78ff68e0f7966c9e8a4e389fbe64a7b31e4e30b88b1141d2089
ENV ALGORITHM_JWT=HS256


CMD ["uvicorn", "app.main:app", "--forwarded-allow-ips", "*", "--host", "0.0.0.0", "--port", "80"]
