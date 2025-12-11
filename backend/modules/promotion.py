"""商品促销分析模块。"""
from typing import Dict, List

import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules

"""商品促销分析模块，包含指标筛选与关联规则挖掘。"""

from backend import config
from backend.api_models import AssociationRule
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
        lambda r: f"销量{int(r['quantity'])}件，利润率{r['profit_rate']:.2f}，折扣{r['discount']:.2f}", axis=1,
    )
    LOGGER.info("筛选得到 %s 个促销候选商品。", len(candidates))
    return candidates.sort_values(by=["profit_rate", "quantity"], ascending=[True, False])


def build_basket_matrix(repo: DataRepository) -> pd.DataFrame:
    """
    将订单明细转换为购物篮 0/1 矩阵。

    :param repo: 数据仓库。
    :return: 订单-商品矩阵，行为订单，列为商品，值为是否购买。
    """
    if repo.raw_df is None:
        raise ValueError("请先加载数据再进行关联分析。")
    df = repo.raw_df[["order_id", "product_id", "quantity"]].dropna()
    if df.empty:
        raise ValueError("销售明细为空，无法生成购物篮。")
    df["flag"] = (df["quantity"] > 0).astype(int)
    pivot = df.pivot_table(index="order_id", columns="product_id", values="flag", fill_value=0, aggfunc="max")
    LOGGER.info("已构建购物篮矩阵，订单数 %s，商品数 %s。", pivot.shape[0], pivot.shape[1])
    return pivot


def mine_association_rules(
    repo: DataRepository,
    min_support: float = config.DEFAULT_MIN_SUPPORT,
    min_confidence: float = config.DEFAULT_MIN_CONFIDENCE,
    metric: str = "lift",
) -> List[AssociationRule]:
    """
    使用 Apriori 挖掘强关联规则。

    :param repo: 数据仓库。
    :param min_support: 最小支持度。
    :param min_confidence: 最小置信度。
    :param metric: 规则排序指标，默认使用提升度。
    :return: 关联规则列表。
    """
    _validate_thresholds(min_support, min_confidence)
    basket = build_basket_matrix(repo)
    rules_df = _mine_with_fallback(basket, min_support, min_confidence, metric)
    if rules_df.empty:
        return []
    id_name_map = _build_product_name_map(repo)
    rules_df = rules_df.sort_values(by=metric, ascending=False)
    return [_format_rule(row, id_name_map, metric) for _, row in rules_df.iterrows()]


def _mine_with_fallback(basket: pd.DataFrame, min_support: float, min_confidence: float, metric: str) -> pd.DataFrame:
    """优先使用用户阈值挖掘，无结果时自动放宽至更低支持度/置信度。"""
    attempts = [(min_support, min_confidence), (max(min_support / 2, 0.001), max(min_confidence * 0.8, 0.1))]
    for support, confidence in attempts:
        frequent = apriori(basket.astype(bool), min_support=support, use_colnames=True)
        if frequent.empty:
            LOGGER.warning("在支持度 %.4f 下未找到频繁项集，尝试放宽阈值。", support)
            continue
        rules_df = association_rules(frequent, metric="confidence", min_threshold=confidence)
        rules_df = rules_df[rules_df[metric] > 1] if metric == "lift" else rules_df
        rules_df = rules_df[(rules_df["antecedents"].apply(len) > 0) & (rules_df["consequents"].apply(len) > 0)]
        if not rules_df.empty:
            LOGGER.info("关联挖掘成功：支持度 %.4f / 置信度 %.2f，获得 %s 条规则。", support, confidence, len(rules_df))
            return rules_df
    LOGGER.warning("放宽阈值后依然未能找到有效关联规则。")
    return pd.DataFrame()


def _validate_thresholds(min_support: float, min_confidence: float) -> None:
    """校验用户输入阈值，避免超出合理范围。"""
    if not 0 < min_support <= 1:
        raise ValueError("最小支持度需在 (0,1] 区间内。")
    if not 0 < min_confidence <= 1:
        raise ValueError("最小置信度需在 (0,1] 区间内。")


def _build_product_name_map(repo: DataRepository) -> Dict[str, str]:
    """创建 product_id 到名称的映射，便于生成可读理由。"""
    if repo.products is None or repo.products.empty:
        return {}
    mapped = repo.products.set_index("product_id")["product_name"].to_dict()
    return {str(pid): name for pid, name in mapped.items()}


def _format_rule(row: pd.Series, id_name_map: Dict[str, str], metric: str) -> AssociationRule:
    """将关联规则行转为前端友好的模型。"""
    antecedents = _to_readable_list(row["antecedents"], id_name_map)
    consequents = _to_readable_list(row["consequents"], id_name_map)
    lift_value = float(row.get("lift", 0))
    confidence_value = float(row.get("confidence", 0))
    support_value = float(row.get("support", 0))
    reason = (
        f"购买{'+'.join(antecedents)}的顾客有 {confidence_value * 100:.1f}% 概率同时购买{'+'.join(consequents)}，"
        f"支持度 {support_value:.2%}，{metric} 为 {float(row.get(metric, 0)):.2f}"
    )
    return AssociationRule(
        antecedents=antecedents,
        consequents=consequents,
        support=support_value,
        confidence=confidence_value,
        lift=lift_value,
        reason=reason,
    )


def _to_readable_list(items: pd.Series | frozenset, id_name_map: Dict[str, str]) -> List[str]:
    """将商品 ID 集合转换为友好的名称列表。"""
    names: List[str] = []
    for item in items:
        item_str = str(item)
        names.append(id_name_map.get(item_str, item_str))
    return names
