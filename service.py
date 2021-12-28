import sys
from os import path
from typing import Set, Dict, IO, Iterable, List, Optional, Tuple, Union, Any
import logging
from urllib.parse import urlparse, parse_qs
import http.server
from http import HTTPStatus
import easyargs
import json


class HTTPHandler(http.server.BaseHTTPRequestHandler):
    def _set_response_ok(self, msg: Any):
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        logger.debug(f"{msg}")
        msg = json.dumps({"msg": msg})
        self.wfile.write(msg.encode("utf-8"))

    def _set_error(self, status: HTTPStatus, msg: Any):
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        logger.error(f"{msg}")
        msg = json.dumps({"err": msg})
        self.wfile.write(msg.encode("utf-8"))

    def _get_params(self) -> Tuple[str, Dict[str, str]]:
        parsed_url = urlparse(self.path)
        # 'keep_blank_values' will enable parameters without a value
        query_params = parse_qs(parsed_url.query, keep_blank_values=True)
        return parsed_url.path, query_params

    def do_GET(self):
        path, query_params = self._get_params()
        msg = f"This is GET path={path} params={query_params}"
        self._set_response_ok(msg)

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", "0"))
        post_data = self.rfile.read(content_length).decode("utf-8")

        path, query_params = self._get_params()
        if not path:
            msg = f"Path is missing in the URL {self.path}"
            self._set_error(HTTPStatus.BAD_REQUEST, msg)
            return

        if not path in ["", "/"]:
            msg = f"I don;t recognize {path}"
            self._set_error(HTTPStatus.BAD_REQUEST, msg)
            return

        msg = f"This is POST path={path} params={query_params}"
        self._set_response_ok(msg)


@easyargs
def main(server_port=8080):
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
    logger = logging.getLogger("")
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)
    sys.exit(main())
