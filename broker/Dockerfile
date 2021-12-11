FROM python:latest
RUN python -m pip install requests okta_jwt_verifier
ADD broker.py /opt
WORKDIR /opt
ENTRYPOINT ["python", "broker.py"]
