"""TEMPORARY blocking-vs-async experiment. Delete after the experiment.

Registered only when app_env == "local" (see create_app).

Results (10 parallel requests, 5s sleep each, one uvicorn worker):
- async def + time.sleep: 50s total, /health stalled 49s. Blocking call froze the loop, so the requests ran one at a time.
- plain def + time.sleep: 5s total, /health instant. FastAPI ran each in a worker thread, so all 10 overlapped.
- await asyncio.sleep / asyncio.to_thread(time.sleep): 5s total, /health instant. Either way the loop stays free.
"""

import asyncio
import time

from fastapi import APIRouter

router = APIRouter(tags=["experiment"])

SLEEP_SECONDS = 5


@router.get("/_slow-bad")
async def slow_bad() -> dict[str, str]:
    # BAD: a blocking call inside `async def` freezes the whole event loop.
    time.sleep(SLEEP_SECONDS)  # noqa: ASYNC251 - deliberately wrong, that's the experiment
    return {"variant": "async def + time.sleep"}


@router.get("/_slow-good")
def slow_good() -> dict[str, str]:
    # Plain `def`: FastAPI runs it in a worker thread, so blocking is isolated.
    time.sleep(SLEEP_SECONDS)
    return {"variant": "def + time.sleep"}


@router.get("/_slow-async")
async def slow_async() -> dict[str, str]:
    # Fix 1: non-blocking sleep; the loop is free while this waits.
    await asyncio.sleep(SLEEP_SECONDS)
    return {"variant": "async def + await asyncio.sleep"}


@router.get("/_slow-thread")
async def slow_thread() -> dict[str, str]:
    # Fix 2: unavoidable blocking call pushed to a thread.
    await asyncio.to_thread(time.sleep, SLEEP_SECONDS)
    return {"variant": "async def + asyncio.to_thread(time.sleep)"}
