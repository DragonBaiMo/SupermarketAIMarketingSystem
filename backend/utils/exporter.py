"""导出工具，负责结果输出为 CSV。"""
from datetime import datetime
from typing import Optional

import pandas as pd

from backend import config
from backend.utils.logger import LOGGER, ensure_dirs


def export_dataframe(df: pd.DataFrame, name: str, directory: Optional[str] = None) -> str:
    """
    将 DataFrame 导出为 CSV 文件。

    :param df: 需要导出的数据框。
    :param name: 文件名称前缀。
    :param directory: 目标目录，默认使用配置的导出目录。
    :return: 导出后的文件路径。
    """
    ensure_dirs()
    target_dir = directory or config.DEFAULT_EXPORT_DIR
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"{target_dir}/{name}_{timestamp}.csv"
    df.to_csv(path, index=False, encoding="utf-8-sig")
    LOGGER.info("数据已导出：%s", path)
    return path
