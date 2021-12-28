import sys
from typing import Dict, Tuple, Any, List, Set
import logging
from urllib.parse import urlparse, parse_qs
import urllib.request
import http.server
from http import HTTPStatus
import easyargs
import json
from collections import namedtuple, deque

Microservice = namedtuple("Microservice", ["ip_address", "ip_port"])
logger = None

# Shortcut: I want to add a custom handler with self.microservices
all_microservices: Dict[str, List[Microservice]] = {}


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

    def _do_registration(self, url_path: str, query_params: Dict[str, str]):
        """
        Add a new node to the dictionary of microservices
        """
        ip_port, ip_address = query_params.get("ip_port", None), query_params.get(
            "ip_address", None
        )
        if not ip_port or not ip_address:
            self._set_error(
                HTTPStatus.BAD_REQUEST,
                f"ip_address/ip_port tuple is missing in the URL parameters {query_params}",
            )
            return

        microservices: Set[Microservice] = all_microservices.get(url_path, set())
        microservice = Microservice(ip_port=ip_port, ip_address=ip_address)
        microservices.add(microservice)
        all_microservices[url_path] = list(microservices)
        self._set_response_ok(f"Added {microservice}")

    def _pick_microservice(self, url_path: str) -> Microservice:
        """
        Check if the path is known. Pick a node from the set, add the node to end of
        # round-robin list
        """
        microservices: List[Microservice] = all_microservices.get(url_path, [])
        if not microservices:
            self._set_error(
                HTTPStatus.BAD_REQUEST, f"Path {url_path} is not registered"
            )
            return

        microservice = microservices[0]

        # rotate the list
        microservices = deque(microservices)
        microservices.rotate(1)
        microservices = list(microservices)

        return microservice

    def _proxy_request(self, microservice: Microservice, url_path: str):
        try:
            # short cut skip processing return status
            urllib.request.urlopen(
                f"http://{microservice.ip_address}:{microservice.ip_port}{url_path}"
            )
        except Exception as e:
            self._set_error(HTTPStatus.INTERNAL_SERVER_ERROR, f"{e}")

        self._set_response_ok(f"I skip the return status at the moment")

    def do_GET(self):
        # Shortcut: assume that all requests are HTTP GET
        url_path, query_params = self._get_params()
        if url_path in ["/register"]:
            self._do_registration(url_path, query_params)
            return

        # forward the query
        micro_service = self._pick_microservice(url_path)
        if micro_service is None:
            return

        self._proxy_request(url_path, query_params)


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
