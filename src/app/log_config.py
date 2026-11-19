import json
import logging
import logging.config
from datetime import datetime, timezone
from typing import Any

from app.middleware import get_request_id

# Attributes every LogRecord has; anything else came from `extra=`.
_STANDARD_ATTRS = set(logging.makeLogRecord({}).__dict__) | {
    "message",
    "asctime",
    "request_id",
    "color_message",
}


class RequestIDFilter(logging.Filter):
    """Stamps the current request id (from the ContextVar) on every record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created, timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
        }
        for key, value in record.__dict__.items():
            if key not in _STANDARD_ATTRS and not key.startswith("_"):
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(level: str = "INFO") -> None:
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {"request_id": {"()": RequestIDFilter}},
            "formatters": {"json": {"()": JSONFormatter}},
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                    # On the handler, so records propagated from any logger get the id.
                    "filters": ["request_id"],
                }
            },
            "root": {"level": level, "handlers": ["console"]},
            # Route uvicorn's loggers through the root JSON handler.
            "loggers": {
                name: {"handlers": [], "propagate": True, "level": level}
                for name in ("uvicorn", "uvicorn.error", "uvicorn.access")
            },
        }
    )
