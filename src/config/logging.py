"""Structured logging configuration using structlog."""

import logging
import sys
import uuid
from contextvars import ContextVar

import structlog

request_id_var: ContextVar[str] = ContextVar("request_id", default="")


def add_request_id(
    logger: logging.Logger, method_name: str, event_dict: dict
) -> dict:
    """Har bir log yozuviga request_id qo'shish."""
    request_id = request_id_var.get("")
    if request_id:
        event_dict["request_id"] = request_id
    return event_dict


def setup_logging(level: str = "INFO") -> None:
    """Structlog ni sozlash.

    JSON format, production uchun mos — log aggregation
    (ELK, Loki, CloudWatch) bilan ishlash uchun ideal.
    """
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            add_request_id,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Standard logging'ni structlog bilan bog'lash
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper()),
    )

    # Uvicorn va boshqa kutubxona loglarini tizimga moslashtirish
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def generate_request_id() -> str:
    """Unikal request ID generatsiya qilish."""
    return str(uuid.uuid4())[:8]


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Structlog logger olish.

    Usage:
        from src.config.logging import get_logger
        logger = get_logger(__name__)
        logger.info("user_created", user_id=user.id, email=user.email)
    """
    return structlog.get_logger(name)
