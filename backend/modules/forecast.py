"""销售与利润预测模块，提供线性回归与 ARIMA 双模型对比。"""
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.arima.model import ARIMA

from backend import config
from backend.data_loader import DataRepository
from backend.utils.logger import LOGGER


def build_sales_timeseries(repo: DataRepository) -> pd.DataFrame:
    """
    按月聚合销售额与利润，并补齐缺失月份。

    :param repo: 数据仓库。
    :return: 含 period、sales、profit 的时间序列数据框，按时间有序且缺失月份补零。
    """
    if repo.raw_df is None:
        raise ValueError("请先加载数据再进行预测。")
    if "order_date" not in repo.raw_df:
        raise ValueError("数据中缺少订单日期，无法聚合。")
    df = repo.raw_df.copy()
    df["period"] = df["order_date"].dt.to_period("M")
    grouped = df.groupby("period").agg(sales=("sales", "sum"), profit=("profit", "sum")).reset_index()
    grouped = grouped.sort_values(by="period")
    completed = _complete_periods(grouped)
    LOGGER.info("已按月聚合销售与利润，共 %s 期（补齐后 %s 期）。", len(grouped), len(completed))
    return completed


def train_and_predict_sales(
    ts_df: pd.DataFrame, months: int = config.DEFAULT_FORECAST_MONTHS,
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, str]]:
    """
    使用线性回归与 ARIMA 两种模型进行预测，通过留出验证自动择优。

    :param ts_df: 历史时间序列数据框。
    :param months: 需要预测的月份数量。
    :return: (历史带索引的数据框, 选定模型的预测数据框, 模型说明)。
    """
    if ts_df.empty:
        raise ValueError("时间序列数据为空，无法预测。")
    history = ts_df.copy()
    history["t"] = range(1, len(history) + 1)

    evaluation = _evaluate_models(history)
    if evaluation["winner"] == "ARIMA":
        arima_result = _arima_forecast(history, months)
        forecast_df = arima_result["forecast"] if arima_result else _linear_regression_forecast(history, months)
    else:
        forecast_df = _linear_regression_forecast(history, months)

    reason = evaluation["reason"]
    LOGGER.info("预测模型选择：%s，理由：%s", evaluation["winner"], reason)
    return history, forecast_df, {"model": evaluation["winner"], "reason": reason}


def summarize_forecast(predict_df: pd.DataFrame, model_info: Dict[str, str]) -> str:
    """生成预测摘要文本，附带模型选择说明。"""
    if predict_df.empty:
        return "暂无预测数据。"
    next_row = predict_df.iloc[0]
    summary = (
        f"预计下期（{next_row['period']}）销售额约为{next_row['sales']:.2f}，利润约为{next_row['profit']:.2f}。"
        f"当前采用 {model_info.get('model', '线性回归')} 模型，{model_info.get('reason', '')}。"
    )
    return summary


def _linear_regression_forecast(history: pd.DataFrame, months: int) -> pd.DataFrame:
    """基于时间索引的线性回归预测。"""
    model_sales = LinearRegression()
    model_profit = LinearRegression()
    model_sales.fit(history[["t"]], history["sales"])
    model_profit.fit(history[["t"]], history["profit"])

    future_t = list(range(len(history) + 1, len(history) + months + 1))
    future_periods = _extend_periods(history["period"].iloc[-1], months)
    predict_df = pd.DataFrame({"period": future_periods, "t": future_t})
    predict_df["sales"] = model_sales.predict(predict_df[["t"]])
    predict_df["profit"] = model_profit.predict(predict_df[["t"]])
    predict_df["model"] = "线性回归"
    LOGGER.info("完成线性回归基线预测，展望 %s 期。", months)
    return predict_df


def _arima_forecast(history: pd.DataFrame, months: int) -> Dict[str, object] | None:
    """尝试使用 ARIMA 捕捉趋势与周期性，失败时返回 None。"""
    if len(history) < 6:
        LOGGER.warning("样本期数不足，跳过 ARIMA 预测。")
        return None
    try:
        sales_model = ARIMA(history["sales"], order=(1, 1, 1)).fit()
        profit_model = ARIMA(history["profit"], order=(1, 1, 1)).fit()
        sales_forecast = sales_model.forecast(steps=months)
        profit_forecast = profit_model.forecast(steps=months)
    except Exception as exc:  # noqa: BLE001
        LOGGER.warning("ARIMA 拟合失败，回退线性回归。原因：%s", exc)
        return None

    future_periods = _extend_periods(history["period"].iloc[-1], months)
    predict_df = pd.DataFrame({
        "period": future_periods,
        "sales": np.round(sales_forecast, 4),
        "profit": np.round(profit_forecast, 4),
        "model": "ARIMA",
    })
    LOGGER.info("ARIMA 模型 AIC：sales %.2f / profit %.2f", sales_model.aic, profit_model.aic)
    return {"forecast": predict_df, "aic": (sales_model.aic + profit_model.aic) / 2}


def _extend_periods(last_period: str, months: int) -> list[str]:
    """根据最后一个 period 扩展未来月份字符串。"""
    last = pd.Period(last_period, freq="M")
    return [str(last + i) for i in range(1, months + 1)]


def _complete_periods(grouped: pd.DataFrame) -> pd.DataFrame:
    """补齐缺失月份，避免模型因时间断档而失真。"""
    if grouped.empty:
        return grouped
    grouped = grouped.copy()
    grouped["period_index"] = pd.PeriodIndex(grouped["period"], freq="M")
    full_range = pd.period_range(start=grouped["period_index"].min(), end=grouped["period_index"].max(), freq="M")
    completed = grouped.set_index("period_index").reindex(full_range)
    completed["sales"] = completed["sales"].fillna(0)
    completed["profit"] = completed["profit"].fillna(0)
    completed["period"] = completed.index.astype(str)
    completed = completed.reset_index(drop=True)
    return completed[["period", "sales", "profit"]]


def _evaluate_models(history: pd.DataFrame) -> Dict[str, str]:
    """使用留出验证比较 ARIMA 与线性回归，输出获胜模型与理由。"""
    if len(history) < 4:
        fallback = _arima_forecast(history, 1)
        return {
            "winner": "ARIMA" if fallback else "线性回归",
            "reason": "样本期数有限，尝试 ARIMA 如失败则回退线性回归。",
        }

    test_size = max(1, min(3, len(history) // 4))
    train_df = history.iloc[:-test_size]
    test_df = history.iloc[-test_size:]

    baseline_pred = _linear_regression_forecast(train_df, test_size)
    baseline_mape = _mape(test_df["sales"], baseline_pred["sales"])

    arima_eval = _arima_forecast(train_df, test_size)
    if arima_eval:
        arima_pred = arima_eval["forecast"]
        arima_mape = _mape(test_df["sales"], arima_pred["sales"])
    else:
        arima_mape = float("inf")

    if arima_mape < baseline_mape:
        return {
            "winner": "ARIMA",
            "reason": f"留出验证显示 ARIMA MAPE={arima_mape:.2%} 优于线性回归的 {baseline_mape:.2%}。",
        }
    if arima_mape == float("inf"):
        return {
            "winner": "线性回归",
            "reason": "ARIMA 未能收敛或样本不足，使用线性回归基线。",
        }
    return {
        "winner": "线性回归",
        "reason": f"留出验证显示线性回归 MAPE={baseline_mape:.2%} 更优于 ARIMA 的 {arima_mape:.2%}。",
    }


def _mape(actual: pd.Series, predict: pd.Series) -> float:
    """计算平均绝对百分比误差，分母为最小 1e-6 以避免除零。"""
    if len(actual) != len(predict) or len(actual) == 0:
        return float("inf")
    denominator = np.maximum(actual.abs(), 1e-6)
    return float(np.mean(np.abs(actual - predict) / denominator))
