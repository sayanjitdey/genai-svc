import re
import uuid
from contextvars import ContextVar

from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

REQUEST_ID_HEADER = "X-Request-ID"

request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)

# Accept only short, header-safe ids so a client can't inject junk into logs.
_VALID_ID = re.compile(r"^[A-Za-z0-9._-]{1,128}$")


def get_request_id() -> str | None:
    return request_id_ctx.get()


class RequestIDMiddleware:
    """Pure ASGI middleware (BaseHTTPMiddleware can lose contextvars)."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        incoming = Headers(scope=scope).get(REQUEST_ID_HEADER)
        request_id = incoming if incoming and _VALID_ID.match(incoming) else uuid.uuid4().hex
        token = request_id_ctx.set(request_id)

        async def send_with_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                MutableHeaders(scope=message)[REQUEST_ID_HEADER] = request_id
            await send(message)

        try:
            await self.app(scope, receive, send_with_id)
        finally:
            request_id_ctx.reset(token)
