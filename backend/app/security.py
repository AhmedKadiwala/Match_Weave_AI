"""Bound POST body memory before FastAPI parses it, including chunked requests."""

from starlette.responses import JSONResponse


class BodyLimitMiddleware:
    def __init__(self, app, max_bytes=1_000_000):
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope.get("method") != "POST":
            return await self.app(scope, receive, send)
        content_length = dict(scope.get("headers", [])).get(b"content-length")
        if content_length:
            try:
                too_large = int(content_length) > self.max_bytes
            except ValueError:
                return await JSONResponse({"detail": "Invalid Content-Length"}, 400)(scope, receive, send)
            if too_large:
                return await JSONResponse({"detail": "Body exceeds 1 MB"}, 413)(scope, receive, send)
        body = bytearray()
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            chunk = message.get("body", b"")
            if len(body) + len(chunk) > self.max_bytes:
                return await JSONResponse({"detail": "Body exceeds 1 MB"}, 413)(scope, receive, send)
            body.extend(chunk)
            if not message.get("more_body", False):
                break
        delivered = False

        async def buffered_receive():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": bytes(body), "more_body": False}
            return await receive()

        return await self.app(scope, buffered_receive, send)
