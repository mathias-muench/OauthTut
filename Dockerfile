FROM python:latest

ADD dummy-web-server.py /opt

WORKDIR /opt

ENTRYPOINT ["python", "dummy-web-server.py"]
