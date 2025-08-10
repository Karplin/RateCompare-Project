import logging
import sys
from app.config.settings import settings


def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(getattr(logging, settings.LOG_LEVEL))

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

    return logger
