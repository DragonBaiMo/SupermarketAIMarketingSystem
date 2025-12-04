"""日志工具，统一中文日志格式。"""
import logging
import os
from typing import Optional

from backend import config


def ensure_dirs() -> None:
    """确保输出目录存在。"""
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    os.makedirs(config.DEFAULT_EXPORT_DIR, exist_ok=True)
    os.makedirs(config.DEFAULT_FIGURE_DIR, exist_ok=True)


def init_logger(level: str = config.LOG_LEVEL, log_file: Optional[str] = config.LOG_FILE) -> logging.Logger:
    """
    初始化全局日志记录器。

    :param level: 日志级别字符串，如"INFO"。
    :param log_file: 日志文件路径，None 时仅输出到控制台。
    :return: 配置完成的 Logger 对象。
    """
    ensure_dirs()
    logger = logging.getLogger("supermarket_ai")
    if logger.handlers:
        return logger
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger


LOGGER = init_logger()
