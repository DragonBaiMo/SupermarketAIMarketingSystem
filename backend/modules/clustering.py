"""客户聚类模块。"""
from typing import Tuple

from typing import Tuple

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from backend import config
from backend.data_loader import DataRepository
from backend.utils.logger import LOGGER


def calc_rfm(repo: DataRepository) -> pd.DataFrame:
    """
    计算 RFM 指标。

    :param repo: 数据仓库。
    :return: 包含 customer_id、R、F、M 的数据框。
    """
    if repo.orders is None:
        raise ValueError("请先加载数据并构建订单数据。")
    latest_date = repo.get_latest_date()
    if latest_date is None:
        raise ValueError("数据集中缺少订单日期。")
    orders = repo.orders.copy()
    orders["days_since"] = (latest_date - orders["order_date"]).dt.days
    rfm = orders.groupby("customer_id").agg(
        R=("days_since", "min"),
        F=("order_id", "nunique"),
        M=("sales", "sum"),
    ).reset_index()
    LOGGER.info("已计算 RFM 指标，共 %s 个客户。", len(rfm))
    return rfm


def kmeans_cluster(rfm_df: pd.DataFrame, k: int = config.DEFAULT_CLUSTER_K) -> Tuple[pd.DataFrame, KMeans]:
    """
    对 RFM 数据执行 KMeans 聚类。

    :param rfm_df: RFM 数据。
    :param k: 聚类数量。
    :return: (带聚类标签的数据框, 训练好的模型)。
    """
    if rfm_df.empty:
        raise ValueError("RFM 数据为空，无法聚类。")
    scaler = StandardScaler()
    features = rfm_df[["R", "F", "M"]]
    scaled = scaler.fit_transform(features)
    model = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = model.fit_predict(scaled)
    rfm_df = rfm_df.copy()
    rfm_df["cluster"] = labels
    LOGGER.info("完成 KMeans 聚类，共 %s 类。", k)
    return rfm_df, model


def explain_clusters(rfm_df: pd.DataFrame) -> pd.DataFrame:
    """
    根据平均 RFM 值输出分群解释。

    :param rfm_df: 带 cluster 列的 RFM 数据。
    :return: 分群描述数据框，包含 cluster、count、R_mean、F_mean、M_mean、label。
    """
    summary = rfm_df.groupby("cluster").agg(
        count=("customer_id", "count"),
        R_mean=("R", "mean"),
        F_mean=("F", "mean"),
        M_mean=("M", "mean"),
    ).reset_index()
    r_threshold = rfm_df["R"].median() if not rfm_df.empty else 0
    f_threshold = rfm_df["F"].median() if not rfm_df.empty else 0
    m_threshold = rfm_df["M"].median() if not rfm_df.empty else 0
    summary["label"] = summary.apply(lambda row: _label_row(row, r_threshold, f_threshold, m_threshold), axis=1)
    LOGGER.info("生成分群解释，共 %s 个群组。", len(summary))
    return summary


def _label_row(row: pd.Series, r_th: float, f_th: float, m_th: float) -> str:
    """根据 R/F/M 均值的相对位置给出业务标签。"""
    recent = row["R_mean"] <= r_th
    high_freq = row["F_mean"] >= f_th
    high_value = row["M_mean"] >= m_th
    if recent and high_freq and high_value:
        return "高价值忠诚客户"
    if recent and high_value:
        return "潜力成长客户"
    if not recent and not high_freq:
        return "沉睡待唤醒客户"
    if high_freq and not high_value:
        return "高频低客单客户"
    return "稳定普通客户"
