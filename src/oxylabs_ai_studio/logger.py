import logging
import sys

# Package logger name
LOGGER_NAME = "oxylabs_ai_studio"

# Default log level
DEFAULT_LOG_LEVEL = logging.INFO


def get_logger(name: str | None = None) -> logging.Logger:
    """Get a logger instance for the SDK."""
    if name is None:
        logger_name = LOGGER_NAME
    # Ensure all loggers are under the package namespace
    elif not name.startswith(LOGGER_NAME):
        logger_name = f"{LOGGER_NAME}.{name}"
    else:
        logger_name = name

    logger = logging.getLogger(logger_name)
    if logger_name != LOGGER_NAME:
        logger.handlers.clear()
        logger.propagate = True
    return logger


def configure_logging(
    level: int = DEFAULT_LOG_LEVEL,
    format_string: str | None = None,
    handler: logging.Handler | None = None,
) -> None:
    """Configure logging for the Oxy Studio AI SDK."""
    logger = logging.getLogger(LOGGER_NAME)
    for existing_handler in logger.handlers[:]:
        logger.removeHandler(existing_handler)

    logger.setLevel(level)
    if handler is None:
        handler = logging.StreamHandler(sys.stderr)

    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False


_default_logger = logging.getLogger(LOGGER_NAME)
if not _default_logger.handlers:
    configure_logging()
