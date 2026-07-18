"""Structured logging configuration."""

import json
import logging
import sys
import uuid
from datetime import datetime
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="")


class JSONFormatter(logging.Formatter):
    """JSON formatida logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        request_id = request_id_var.get("")
        if request_id:
            log_entry["request_id"] = request_id

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        extra_fields = getattr(record, "extra_fields", {})
        if extra_fields:
            log_entry.update(extra_fields)

        return json.dumps(log_entry, ensure_ascii=False)


def setup_logging(level: str = "INFO") -> None:
    """Loggerni sozlash."""
    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper()))

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    root.handlers = [handler]

    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)


def generate_request_id() -> str:
    """Unikal request ID generatsiya qilish."""
    return str(uuid.uuid4())[:8]


def log_with_context(
    logger: logging.Logger,
    level: str,
    message: str,
    **kwargs,
) -> None:
    """Kontekst bilan logging."""
    extra_fields = {k: v for k, v in kwargs.items() if v is not None}

    record = logger.makeRecord(
        name=logger.name,
        level=getattr(logging, level.upper()),
        fn="",
        lno=0,
        msg=message,
        args=(),
        exc_info=None,
    )
    record.extra_fields = extra_fields

    logger.handle(record)
