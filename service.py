import sys
from os import path
from typing import Set, Dict, IO, Iterable, List, Optional, Tuple, Union
import logging
from urllib.parse import urlparse, parse_qs
import http.server
import easyargs
import json


class HTTPHandler(http.server.BaseHTTPRequestHandler):
    def _set_response_ok(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def _set_error(self, msg):
        logger.error(msg)
        msg = json.dumps({"err": msg})

        self.send_response(400)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(msg.encode("utf-8"))

    def do_GET(self):
        msg = (f"This is GET {self.path}")
        self.wfile.write(msg.encode("utf-8"))
        self._set_response_ok()

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", "0"))
        post_data = self.rfile.read(content_length).decode("utf-8")

        parsed_url = urlparse(self.path)
        if not parsed_url.path:
            msg = f"Path is missing in the URL {self.path}"
            self._set_error(msg)
            return

        if not parsed_url.path in ["", "/"]:
            msg = f"I don;t recognize {parsed_url.path}"
            self._set_error(msg)
            return

        # 'keep_blank_values' will enable parameters without a value
        query_params = parse_qs(parsed_url.query, keep_blank_values=True)
        msg = (f"This is POST path={parsed_url.path} params={query_params}")
        self.wfile.write(msg.encode("utf-8"))
        self._set_response_ok()


@easyargs
def main(server_port=38080):
    server_address = ("", server_port)
    httpd = http.server.HTTPServer(server_address, HTTPHandler)
    logger.info(f"Starting httpd {server_address}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.error("I got Ctrl-C")
    finally:
        logger.info(f"Closing httpd {server_address}")
        httpd.server_close()
    return 0


if __name__ == "__main__":
    logger = logging.getLogger()
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)
    sys.exit(main())
