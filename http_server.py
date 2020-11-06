#!python3
# Copyright (c) 2020 Ted Miller. All rights reserved.

from http.server import BaseHTTPRequestHandler, HTTPServer

class MyHttpRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        print("*** POST")
        print(f"REQUEST: {self.request}")
        print(f"HEADERS: {self.headers}")
        print(f"COMMAND: {self.command}")
        print(f"PATH: {self.path}")         # need this

        payloadLength = int(self.headers.get("Content-Length"))
        data = self.rfile.read(payloadLength).decode("utf-8");
        print(f"DATA: {data}")

        print("(END)")
        self.send_response(200)
        self.end_headers()

server_address = ('', 5556)
httpd = HTTPServer(server_address, MyHttpRequestHandler)
while True:
    httpd.handle_request()
