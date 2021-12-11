#!/usr/bin/env python

from http.cookies import SimpleCookie
from http.server import HTTPServer, BaseHTTPRequestHandler
from oauthlib.oauth2 import WebApplicationClient
from okta_jwt_verifier import JWTVerifier
import asyncio
import logging
import os
import requests

client_id = None
client_secret = None


class myHTTPRequestHandler(BaseHTTPRequestHandler):
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

    def _login(self):
        okta = WebApplicationClient(client_id)
        authorization_base_url = okta_domain + "/oauth2/default/v1/authorize"
        authorization_url = okta.prepare_request_uri(
            authorization_base_url,
            redirect_uri="http://localhost:8080/callback",
            state="bla",
            scope="openid",
        )
        self.send_response(302)
        self.send_header("Location", authorization_url)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(
            "<html><body><p>Redirecting...</p></body></html>".encode("utf8")
        )

    def _callback(self):
        okta = WebApplicationClient(client_id)
        okta.parse_request_uri_response(self.path)
        data = okta.prepare_request_body(
            redirect_uri="http://localhost:8080/callback",
            client_secret=client_secret,
        )
        logging.debug(data)

        token_url = okta_domain + "/oauth2/default/v1/token"
        headers = {
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded",
        }
        response = requests.post(token_url, headers=headers, data=data)
        okta.parse_request_body_response(response.text)
        logging.debug(okta.token)

        cookies = SimpleCookie()
        cookies["access_token"] = okta.token["access_token"]
        self.send_response(302)
        self.send_header("Set-Cookie", cookies["access_token"].OutputString())
        self.send_header("Location", "/")
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write("<html><body><p>Logged in!</p></body></html>".encode("utf8"))

    def _portal_page(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(
            '<html><body><p>Hi, I\'m the <em>portal</em>, <a href="http://localhost:8888/">open device page</a></p></body></html>'.encode(
                "utf8"
            )
        )

    def _unauthorized_page(self):
        self.send_response(401)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(
            "<html><body><p>Unauthorized!</p></body></html>".encode("utf8")
        )

    def do_GET(self):
        if self.path == "/login":
            self._login()
        elif self.path.startswith("/callback?"):
            self._callback()
        else:
            if self._is_authorized():
                self._portal_page()
            else:
                self._unauthorized_page()


if __name__ == "__main__":
    client_id = os.environ["OT_CLIENT_ID"]
    client_secret = os.environ["OT_CLIENT_SECRET"]
    okta_domain = os.environ["OT_OKTA_DOMAIN"]
    logging.basicConfig(level=os.environ.get("OT_LOGLEVEL", "INFO"))
    HTTPServer(("0.0.0.0", 8080), myHTTPRequestHandler).serve_forever()
