"""商品促销分析模块。"""
from typing import Dict

from typing import Dict

import pandas as pd

from backend import config
from backend.data_loader import DataRepository
from backend.utils.logger import LOGGER


def calc_product_metrics(repo: DataRepository) -> pd.DataFrame:
    """
    计算商品销售指标。

    :param repo: 数据仓库实例。
    :return: 包含销量、销售额、利润率等指标的商品数据框。
    """
    if repo.raw_df is None:
        raise ValueError("请先加载数据再计算商品指标。")
    products = repo.products
    if products is None:
        raise ValueError("商品汇总数据不存在。")
    LOGGER.info("已生成商品指标，共 %s 个商品。", len(products))
    return products


def select_promotion_candidates(products: pd.DataFrame, rule: Dict[str, float] | None = None) -> pd.DataFrame:
    """
    根据规则筛选促销候选商品。

    :param products: 商品指标数据框。
    :param rule: 促销规则，包括 min_quantity、max_quantity、min_profit_rate、max_discount。
    :return: 符合条件的促销商品列表。
    """
    if rule is None:
        rule = config.DEFAULT_PROMOTION_RULE
    LOGGER.info("使用促销规则：%s", rule)
    candidates = products[
        (products["quantity"] >= rule.get("min_quantity", 0))
        & (products["quantity"] <= rule.get("max_quantity", float("inf")))
        & (products["profit_rate"] >= rule.get("min_profit_rate", 0))
        & (products["discount"] <= rule.get("max_discount", 1))
    ].copy()
    candidates["reason"] = candidates.apply(
        lambda r: f"销量{int(r['quantity'])}件，利润率{r['profit_rate']:.2f}，折扣{r['discount']:.2f}", axis=1
    )
    LOGGER.info("筛选得到 %s 个促销候选商品。", len(candidates))
    return candidates.sort_values(by=["profit_rate", "quantity"], ascending=[True, False])
