import asyncio
import logging
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from app.security import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/v1/stream",
    tags=["stream"],
    dependencies=[Depends(get_current_user)],
)

EVENT_COUNT = 10
EVENT_INTERVAL_SECONDS = 0.5


def _sse_data(text: str) -> str:
    # A bare newline would end the event early, so each line gets its own
    # "data:" field; the client rejoins them with "\n".
    lines = text.splitlines() or [""]
    return "".join(f"data: {line}\n" for line in lines) + "\n"


async def _echo_events(message: str) -> AsyncIterator[str]:
    sent = 0
    try:
        for i in range(1, EVENT_COUNT + 1):
            yield _sse_data(f"{i}/{EVENT_COUNT}: {message}")
            sent += 1
            if i < EVENT_COUNT:
                await asyncio.sleep(EVENT_INTERVAL_SECONDS)
    except asyncio.CancelledError:
        # Starlette cancels the streaming task when the client goes away.
        # Log, then re-raise so the cancellation propagates and the stream stops.
        logger.info(
            "client disconnected, stopping stream",
            extra={"events_sent": sent, "events_total": EVENT_COUNT},
        )
        raise


@router.get("/echo")
async def echo(
    message: Annotated[str, Query(max_length=200)] = "hello",
) -> StreamingResponse:
    return StreamingResponse(
        _echo_events(message),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
