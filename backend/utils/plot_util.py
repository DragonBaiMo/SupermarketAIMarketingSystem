"""绘图工具，统一输出目录与格式。"""
from typing import List, Optional

import matplotlib.pyplot as plt
import pandas as pd

from backend import config
from backend.utils.logger import LOGGER, ensure_dirs


def plot_sales_forecast(history_df: pd.DataFrame, predict_df: pd.DataFrame, value_col: str, title: str, filename: str) -> str:
    """
    绘制历史与预测曲线并保存。

    :param history_df: 历史数据 DataFrame，需包含 period 与 value_col。
    :param predict_df: 预测数据 DataFrame，需包含 period 与 value_col。
    :param value_col: 数值列名，如 "sales" 或 "profit"。
    :param title: 图表标题。
    :param filename: 输出文件名。
    :return: 图表文件路径。
    """
    ensure_dirs()
    plt.figure(figsize=(8, 4))
    plt.plot(history_df["period"], history_df[value_col], marker="o", label="历史值")
    plt.plot(predict_df["period"], predict_df[value_col], marker="x", linestyle="--", label="预测值")
    plt.title(title)
    plt.xlabel("期数")
    plt.ylabel(value_col)
    plt.legend()
    plt.grid(True)
    path = _figure_path(filename)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    LOGGER.info("图表已保存：%s", path)
    return path


def plot_cluster_distribution(cluster_df: pd.DataFrame, filename: str, title: str = "客户分群占比") -> str:
    """绘制客户分群饼图。"""
    ensure_dirs()
    plt.figure(figsize=(6, 6))
    plt.pie(cluster_df["count"], labels=cluster_df["cluster"], autopct="%1.1f%%", startangle=90)
    plt.title(title)
    path = _figure_path(filename)
    plt.savefig(path)
    plt.close()
    LOGGER.info("分群饼图已保存：%s", path)
    return path


def _figure_path(filename: str) -> str:
    ensure_dirs()
    return f"{config.DEFAULT_FIGURE_DIR}/{filename}"
