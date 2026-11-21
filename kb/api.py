"""Minimal stdlib HTTP server exposing the grounded ``POST /chat`` endpoint."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .chat import handle_chat


class ChatHandler(BaseHTTPRequestHandler):
    server_version = "LocalityKnowledgeBase/0.1"

    def _send(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.split("?")[0] == "/health":
            self._send(200, {"status": "ok"})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path.split("?")[0] != "/chat":
            self._send(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            self._send(200, handle_chat(payload))
        except (ValueError, UnicodeDecodeError) as error:
            self._send(400, {"error": str(error)})

    def log_message(self, format, *args):
        pass


def serve(host="127.0.0.1", port=8000):
    server = ThreadingHTTPServer((host, port), ChatHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return server
