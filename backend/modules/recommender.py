"""客户推荐模块。"""
from typing import Dict

import pandas as pd

from backend import config
from backend.data_loader import DataRepository
from backend.utils.logger import LOGGER


class Recommender:
    """基于购买频次和共现的简单推荐器。"""

    def __init__(self, repo: DataRepository) -> None:
        self.repo = repo

    def get_customer_history(self, customer_id: str) -> pd.DataFrame:
        """
        获取客户历史购物记录。

        :param customer_id: 客户编号。
        :return: 该客户的订单明细。
        """
        if self.repo.raw_df is None:
            raise ValueError("请先加载数据再进行推荐。")
        df = self.repo.raw_df
        target = str(customer_id).strip()
        return df[df["customer_id"].astype(str) == target]

    def recommend(self, customer_id: str, top_n: int = config.DEFAULT_TOP_N) -> pd.DataFrame:
        """
        生成客户的推荐商品列表。

        :param customer_id: 客户编号。
        :param top_n: 推荐数量。
        :return: 推荐商品 DataFrame，包含 product_id、score 与推荐理由。
        """
        if self.repo.raw_df is None:
            raise ValueError("请先加载数据再进行推荐。")
        if not str(customer_id).strip():
            raise ValueError("客户编号不能为空。")
        user_df = self.get_customer_history(customer_id)
        if user_df.empty:
            LOGGER.warning("客户 %s 暂无历史订单，拒绝返回随机推荐。", customer_id)
            raise ValueError("未找到该客户历史订单，请输入有效客户编号。")
        co_matrix = self._build_co_occurrence()
        scores: Dict[str, float] = {}
        purchased = set(user_df["product_id"].unique())
        for product in purchased:
            neighbors = co_matrix.get(product, {})
            for item, weight in neighbors.items():
                if item in purchased:
                    continue
                scores[item] = scores.get(item, 0) + weight
        if not scores:
            return self._global_top_products(top_n)
        score_df = pd.DataFrame([{"product_id": pid, "score": score} for pid, score in scores.items()])
        products = self.repo.products if self.repo.products is not None else pd.DataFrame(columns=["product_id", "product_name"])
        merged = score_df.merge(products[["product_id", "product_name"]], on="product_id", how="left")
        merged["reason"] = "同购商品共现度高，适合推荐"
        merged = merged.sort_values(by="score", ascending=False).head(top_n)
        return merged

    def _build_co_occurrence(self) -> Dict[str, Dict[str, float]]:
        """计算商品共现矩阵，用于共现推荐。"""
        if self.repo.raw_df is None:
            return {}
        co_matrix: Dict[str, Dict[str, float]] = {}
        grouped = self.repo.raw_df.groupby("order_id")
        for _, group in grouped:
            items = group["product_id"].dropna().unique()
            for i, item_i in enumerate(items):
                co_matrix.setdefault(item_i, {})
                for j, item_j in enumerate(items):
                    if i == j:
                        continue
                    co_matrix[item_i][item_j] = co_matrix[item_i].get(item_j, 0) + 1
        return co_matrix

    def _global_top_products(self, top_n: int) -> pd.DataFrame:
        """按销量返回全局热销商品。"""
        if self.repo.products is None:
            raise ValueError("尚未生成商品指标，无法推荐。")
        df = self.repo.products.copy()
        df = df.sort_values(by="quantity", ascending=False).head(top_n)
        df["reason"] = "基于全局热销度推荐"
        df["score"] = df["quantity"]
        return df[["product_id", "product_name", "score", "reason"]]
