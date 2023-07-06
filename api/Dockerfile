FROM python:3.6-slim
COPY . /app
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install setuptools==46.1.3

RUN set -ex \
  && apt-get -y update \
  && apt-get -y install --reinstall libpq-dev

RUN pip install -r requirements.txt
EXPOSE 5000
ENTRYPOINT [ "python" ]
CMD [ "app.py" ]
