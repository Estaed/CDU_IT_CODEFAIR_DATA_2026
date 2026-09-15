"""Signalling scaffold for the WebRTC hotspot spike.

Serves index.html and relays SDP offer/answer JSON blobs between two phones so
they can open a direct WebRTC DataChannel. This server is test scaffolding
only: in production the handshake is done by QR codes, not by this relay.
"""

import argparse
import json
import socket
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
INDEX_HTML = HERE / "index.html"

_store_lock = threading.Lock()
_store: dict[str, str] = {}


def _local_ipv4_addresses() -> list[str]:
    """Return every non-loopback IPv4 address bound on this machine."""
    addresses: set[str] = set()
    hostname = socket.gethostname()
    try:
        for _family, _kind, _proto, _name, sockaddr in socket.getaddrinfo(
            hostname, None, socket.AF_INET
        ):
            ip = sockaddr[0]
            if not ip.startswith("127."):
                addresses.add(ip)
    except OSError:
        pass
    try:
        probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # A UDP connect only asks the OS to pick a route; no packet is sent.
            probe.connect(("8.8.8.8", 80))
            ip = probe.getsockname()[0]
            if not ip.startswith("127."):
                addresses.add(ip)
        finally:
            probe.close()
    except OSError:
        pass
    return sorted(addresses)


class SignallingHandler(BaseHTTPRequestHandler):
    """Serves index.html and relays /offer, /answer, /reset as raw JSON text."""

    server_version = "SpikeSignalling/1.0"

    def _send_json_text(self, status: HTTPStatus, body: str | None) -> None:
        payload = b"" if not body else body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        if payload:
            self.wfile.write(payload)

    def _send_file(self, path: Path, content_type: str) -> None:
        body = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> str:
        length = int(self.headers.get("Content-Length", "0"))
        return self.rfile.read(length).decode("utf-8") if length else ""

    def do_GET(self) -> None:
        try:
            if self.path in ("/", "/index.html"):
                self._send_file(INDEX_HTML, "text/html; charset=utf-8")
                return
            if self.path in ("/offer", "/answer"):
                key = self.path.strip("/")
                with _store_lock:
                    value = _store.get(key)
                if value is None:
                    self._send_json_text(HTTPStatus.NO_CONTENT, None)
                else:
                    self._send_json_text(HTTPStatus.OK, value)
                return
            self._send_json_text(HTTPStatus.NOT_FOUND, json.dumps({"error": "not found"}))
        except OSError:
            pass

    def do_POST(self) -> None:
        try:
            if self.path in ("/offer", "/answer"):
                key = self.path.strip("/")
                body = self._read_body()
                with _store_lock:
                    _store[key] = body
                self._send_json_text(HTTPStatus.OK, json.dumps({"ok": True}))
                return
            if self.path == "/reset":
                with _store_lock:
                    _store.clear()
                self._send_json_text(HTTPStatus.OK, json.dumps({"ok": True}))
                return
            self._send_json_text(HTTPStatus.NOT_FOUND, json.dumps({"error": "not found"}))
        except OSError:
            pass

    def log_message(self, format_str: str, *args: object) -> None:
        print(f"{self.address_string()} {self.command} {self.path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="WebRTC hotspot spike signalling server.")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    server = ThreadingHTTPServer(("0.0.0.0", args.port), SignallingHandler)
    print("WebRTC hotspot spike signalling server")
    print(f"Serving {INDEX_HTML}")
    for ip in _local_ipv4_addresses():
        print(f"Open on both phones: http://{ip}:{args.port}/")
    print("Ctrl+C to stop (the DataChannel keeps working after this server dies).")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
