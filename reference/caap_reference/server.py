"""HTTP/JSON binding for the CAAP research broker."""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

from .broker import Broker, CaapError


MAX_BODY = 1024 * 1024


def make_handler(broker: Broker, auth_token: str | None = None):
    class Handler(BaseHTTPRequestHandler):
        server_version = "CAAPReference/0.2"

        def do_GET(self) -> None:  # noqa: N802
            try:
                self._authenticate()
                path = urlparse(self.path).path
                if path == "/healthz":
                    self._send(200, {"status": "ok"})
                elif path == "/v1/capabilities":
                    self._send(200, broker.capabilities(self._tenant()))
                elif path.startswith("/v1/keys/"):
                    self._send(200, broker.read_key(unquote(path.removeprefix("/v1/keys/")), self._tenant()))
                else:
                    self._send(404, CaapError("INVALID_REQUEST", "route not found", status=404).response())
            except CaapError as exc:
                self._send(exc.status, exc.response())

        def do_POST(self) -> None:  # noqa: N802
            try:
                self._authenticate()
                route_operation = {"/v1/policies:resolve": "ResolvePolicy", "/v1/keys": "CreateKey", "/v1/sign": "Sign", "/v1/verify": "Verify"}.get(urlparse(self.path).path)
                if route_operation is None:
                    raise CaapError("INVALID_REQUEST", "route not found", status=404)
                request = self._read_json()
                if request.get("operation") != route_operation:
                    raise CaapError("INVALID_REQUEST", "operation does not match route")
                status, response = broker.execute(request, self._tenant())
                self._send(status, response)
            except CaapError as exc:
                self._send(exc.status, exc.response())

        def _authenticate(self) -> None:
            if auth_token and self.headers.get("Authorization") != f"Bearer {auth_token}":
                raise CaapError("UNAUTHENTICATED", "valid bearer credential required", status=401)

        def _tenant(self) -> str:
            value = self.headers.get("X-CAAP-Tenant", "local-dev")
            if not value or len(value) > 128 or not all(c.isalnum() or c in "._-" for c in value):
                raise CaapError("INVALID_REQUEST", "invalid development tenant")
            return value

        def _read_json(self):
            content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip()
            if content_type != "application/json":
                raise CaapError("INVALID_REQUEST", "Content-Type must be application/json", status=415)
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError as exc:
                raise CaapError("INVALID_REQUEST", "invalid Content-Length") from exc
            if length <= 0 or length > MAX_BODY:
                raise CaapError("INVALID_REQUEST", "request body size is invalid", status=413)
            try:
                return json.loads(self.rfile.read(length))
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                raise CaapError("INVALID_REQUEST", "request body is not valid JSON") from exc

        def _send(self, status: int, value) -> None:
            body = json.dumps(value, separators=(",", ":")).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args) -> None:
            print(f"{self.address_string()} {format % args}")

    return Handler


def main() -> None:
    host = os.getenv("CAAP_HOST", "127.0.0.1")
    port = int(os.getenv("CAAP_PORT", "8080"))
    auth_token = os.getenv("CAAP_AUTH_TOKEN") or None
    server = ThreadingHTTPServer((host, port), make_handler(Broker(), auth_token))
    print(f"CAAP research server listening on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
