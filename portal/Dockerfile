FROM python:latest
RUN python -m pip install requests oauthlib okta_jwt_verifier
ADD portal.py /opt
WORKDIR /opt
ENTRYPOINT ["python", "portal.py"]
