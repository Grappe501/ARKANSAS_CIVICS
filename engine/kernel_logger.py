from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import logging


_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class KernelLogger:
    def __init__(self, name: str, logs_dir: Path, level: str = "INFO") -> None:
        self.logs_dir = logs_dir
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        self.logger.propagate = False

        if not self.logger.handlers:
            formatter = logging.Formatter(_FORMAT)

            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            self.logger.addHandler(stream_handler)

            file_handler = logging.FileHandler(self.logs_dir / f"{name}.log", encoding="utf-8")
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def debug(self, message: str) -> None:
        self.logger.debug(message)

    def info(self, message: str) -> None:
        self.logger.info(message)

    def warning(self, message: str) -> None:
        self.logger.warning(message)

    def error(self, message: str) -> None:
        self.logger.error(message)


def get_kernel_logger(name: str, logs_dir: Path, level: str = "INFO") -> KernelLogger:
    return KernelLogger(name=name, logs_dir=logs_dir, level=level)
