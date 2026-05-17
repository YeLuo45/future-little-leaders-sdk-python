"""Webhook server and signature verification for fll_sdk."""

import hashlib
import hmac
import json
from typing import Callable, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

from fll_sdk.models import WebhookEvent


def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verify a webhook signature.

    Args:
        payload: Raw request body bytes.
        signature: Value from X-FLL-Signature header (format: sha256=<hex>).
        secret: Webhook secret used for HMAC.

    Returns:
        True if signature is valid, False otherwise.
    """
    if not signature.startswith('sha256='):
        return False

    expected = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()

    received = signature[7:]  # strip 'sha256=' prefix
    return hmac.compare_digest(expected, received)


class WebhookServer:
    """
    Standalone webhook receiver server.

    Example usage:
        def on_task_completed(event):
            print(f"Task {event.data['task_id']} completed")

        server = WebhookServer(secret='my-webhook-secret')
        server.register('task.completed', on_task_completed)
        server.run(port=5000)
    """

    def __init__(self, secret: str, host: str = '0.0.0.0'):
        """
        Initialize webhook server.

        Args:
            secret: Secret key for signature verification.
            host: Host to bind to.
        """
        self.secret = secret
        self.host = host
        self._handlers: dict[str, list[Callable]] = {}
        self._server: Optional[HTTPServer] = None
        self._thread: Optional[threading.Thread] = None

    def register(self, event: str, handler: Callable[[WebhookEvent], None]) -> None:
        """
        Register a handler for a webhook event.

        Args:
            event: Event name (e.g., 'task.completed').
            handler: Callback function that accepts a WebhookEvent.
        """
        if event not in self._handlers:
            self._handlers[event] = []
        self._handlers[event].append(handler)

    def _handle_request(self, handler: BaseHTTPRequestHandler) -> None:
        """Handle incoming webhook request."""
        import logging

        content_length = int(handler.headers.get('Content-Length', 0))
        body = handler.rfile.read(content_length)

        # Verify signature
        signature = handler.headers.get('X-FLL-Signature', '')
        if not verify_signature(body, signature, self.secret):
            handler.send_response(401)
            handler.end_headers()
            handler.wfile.write(b'Invalid signature')
            return

        try:
            data = json.loads(body.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            handler.send_response(400)
            handler.end_headers()
            handler.wfile.write(b'Invalid JSON body')
            return

        event = WebhookEvent(**data)
        handlers = self._handlers.get(event.event, [])

        for h in handlers:
            try:
                h(event)
            except Exception as e:
                logging.error(f'Webhook handler error: {e}')

        handler.send_response(200)
        handler.end_headers()
        handler.wfile.write(b'OK')

    def run(self, port: int = 5000, blocking: bool = True) -> None:
        """
        Start the webhook server.

        Args:
            port: Port to listen on.
            blocking: If True, blocks the current thread.
        """
        class _WebhookHandler(BaseHTTPRequestHandler):
            def do_POST(self):
                self.server._parent._handle_request(self)

            def log_message(self, format, *args):
                pass  # suppress request logging

        class _Server(HTTPServer):
            def __init__(self, server_address, RequestHandlerClass, _parent):
                super().__init__(server_address, RequestHandlerClass)
                self._parent = _parent

        self._server = _Server((self.host, port), _WebhookHandler, self)

        if blocking:
            print(f'Webhook server listening on {self.host}:{port}')
            self._server.serve_forever()
        else:
            self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
            self._thread.start()

    def stop(self) -> None:
        """Stop the webhook server."""
        if self._server:
            self._server.shutdown()
            self._server = None