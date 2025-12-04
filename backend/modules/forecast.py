"""销售与利润预测模块。"""
from typing import Tuple

from typing import Tuple

import pandas as pd
from sklearn.linear_model import LinearRegression

from backend import config
from backend.data_loader import DataRepository
from backend.utils.logger import LOGGER


def build_sales_timeseries(repo: DataRepository) -> pd.DataFrame:
    """
    按月聚合销售额与利润。

    :param repo: 数据仓库。
    :return: 含 period、sales、profit 的时间序列数据框。
    """
    if repo.raw_df is None:
        raise ValueError("请先加载数据再进行预测。")
    if "order_date" not in repo.raw_df:
        raise ValueError("数据中缺少订单日期，无法聚合。")
    df = repo.raw_df.copy()
    df["period"] = df["order_date"].dt.to_period("M").astype(str)
    grouped = df.groupby("period").agg(sales=("sales", "sum"), profit=("profit", "sum")).reset_index()
    LOGGER.info("已按月聚合销售与利润，共 %s 期。", len(grouped))
    return grouped.sort_values(by="period")


def train_and_predict_sales(ts_df: pd.DataFrame, months: int = config.DEFAULT_FORECAST_MONTHS) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    训练线性回归模型并预测未来月份销售额与利润。

    :param ts_df: 历史时间序列数据框。
    :param months: 需要预测的月份数量。
    :return: (历史带索引的数据框, 预测数据框)。
    """
    if ts_df.empty:
        raise ValueError("时间序列数据为空，无法预测。")
    history = ts_df.copy()
    history["t"] = range(1, len(history) + 1)
    model_sales = LinearRegression()
    model_profit = LinearRegression()
    model_sales.fit(history[["t"]], history["sales"])
    model_profit.fit(history[["t"]], history["profit"])

    future_t = list(range(len(history) + 1, len(history) + months + 1))
    future_periods = _extend_periods(history["period"].iloc[-1], months)
    predict_df = pd.DataFrame({
        "period": future_periods,
        "t": future_t,
    })
    predict_df["sales"] = model_sales.predict(predict_df[["t"]])
    predict_df["profit"] = model_profit.predict(predict_df[["t"]])
    LOGGER.info("完成未来 %s 个月的销售与利润预测。", months)
    return history, predict_df


def summarize_forecast(predict_df: pd.DataFrame) -> str:
    """生成预测摘要文本。"""
    if predict_df.empty:
        return "暂无预测数据。"
    next_row = predict_df.iloc[0]
    summary = f"预计下期（{next_row['period']}）销售额约为{next_row['sales']:.2f}，利润约为{next_row['profit']:.2f}。"
    return summary


def _extend_periods(last_period: str, months: int) -> list[str]:
    """根据最后一个 period 扩展未来月份字符串。"""
    last = pd.Period(last_period, freq="M")
    return [str(last + i) for i in range(1, months + 1)]
