from collections import namedtuple
import sys
from typing import Dict, Tuple, Any, Set
import logging
from urllib.parse import urlparse, parse_qs
import http.server
from http import HTTPStatus
import easyargs
import json
import requests
from collections import namedtuple

Microservice = namedtuple("Microservice", ["ip_address", "ip_port"])


class HTTPHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self):
        super().__init__(self)
        self.microservices: Set[str, Microservice] = set()

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

    def do_registration(self, url_path: str, query_params: Dict[str, str]):
        if not "ip_port" in query_params:
            self._set_error(
                HTTPStatus.BAD_REQUEST,
                f"ip_port is missing in the URL parameters {query_params}",
            )
            return

        if not "ip_address" in query_params:
            self._set_error(
                HTTPStatus.BAD_REQUEST,
                f"ip_address is missing in the URL parameters {query_params}",
            )
            return

        self.microservices.add(Microservice(ip_port=ip_port, ip_address=ip_address))

    def do_GET(self):
        # Shortcut: assume that all requests are HTTP GET
        url_path, query_params = self._get_params()
        if url_path in ["/register"]:
            self._do_registration(url_path, query_params)
            return

        # forward the query
        micro_service, msg = self._pcik_microservice(url_path)
        if micro_service is None:
            self._set_error(f"msg")
            return

        self.send_query(url_path, query_params)


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
