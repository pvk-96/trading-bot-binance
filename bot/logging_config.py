import logging
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_FILE = LOG_DIR / "trading_bot.log"
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(level=logging.INFO):
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("trading_bot")

    if logger.handlers:
        return logger

    logger.setLevel(level)

    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setLevel(level)
    fh.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    logger.addHandler(ch)

    return logger
