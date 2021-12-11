#!/usr/bin/env python

from http.cookies import SimpleCookie
from http.server import HTTPServer, BaseHTTPRequestHandler
from okta_jwt_verifier import JWTVerifier
import asyncio
import logging
import os
import requests

client_id = None


class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def _is_authorized(self):
        R = bool()
        cookies = SimpleCookie()
        if "Cookie" in self.headers:
            cookies.load(self.headers.get("Cookie"))
        if "access_token" in cookies:
            try:
                jwt_verifier = JWTVerifier(okta_domain + "/oauth2/default", client_id)
                coroutine = jwt_verifier.verify_access_token(
                    cookies["access_token"].value
                )
                asyncio.run(coroutine)
                R = True
            except:
                R = False
        else:
            R = False
        return R

    def _broker_page(self):
        response = requests.get(url="http://localhost:8000" + self.path)
        self.send_response(response.status_code)
        for k, v in response.headers.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(response.text.encode("utf8"))

    def _unauthorized_page(self):
        self.send_response(401)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(
            "<html><body><p>Unauthorized!</p></body></html>".encode("utf8")
        )

    def do_GET(self):
        if self._is_authorized():
            self._broker_page()
        else:
            self._unauthorized_page()


if __name__ == "__main__":
    client_id = os.environ["OT_CLIENT_ID"]
    okta_domain = os.environ["OT_OKTA_DOMAIN"]
    logging.basicConfig(level=os.environ.get("OT_LOGLEVEL", "INFO"))
    HTTPServer(("0.0.0.0", 8888), MyHTTPRequestHandler).serve_forever()
