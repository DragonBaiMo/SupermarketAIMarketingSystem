"""数据加载与清洗模块。"""
from datetime import datetime
from typing import Dict, Optional

import pandas as pd

from backend import config
from backend.utils.logger import LOGGER


class DataRepository:
    """数据仓库，集中存储加载后的数据视图。"""

    def __init__(self) -> None:
        self.raw_df: Optional[pd.DataFrame] = None
        self.orders: Optional[pd.DataFrame] = None
        self.customers: Optional[pd.DataFrame] = None
        self.products: Optional[pd.DataFrame] = None
        self.source_path: Optional[str] = None

    def load_csv(self, path: str = config.DEFAULT_CSV) -> None:
        """
        读取并清洗销售明细数据。

        :param path: CSV 文件路径。
        """
        LOGGER.info("开始读取销售数据：%s", path)
        try:
            df = pd.read_csv(path)
        except FileNotFoundError as exc:
            LOGGER.error("未找到数据文件，请检查路径：%s", path)
            raise exc
        except PermissionError as exc:
            LOGGER.error("无权限读取文件：%s", path, exc_info=True)
            raise exc
        except pd.errors.EmptyDataError as exc:
            LOGGER.error("CSV 文件为空：%s", path, exc_info=True)
            raise exc
        except pd.errors.ParserError as exc:
            LOGGER.error("CSV 解析失败，文件格式可能不正确：%s", path, exc_info=True)
            raise exc
        except UnicodeDecodeError as exc:
            LOGGER.error("CSV 文件编码错误，请确认文件编码：%s", path, exc_info=True)
            raise exc
        except ValueError as exc:
            LOGGER.error("CSV 数据值异常：%s", path, exc_info=True)
            raise exc

        df = self._normalize_columns(df)
        df = self._convert_types(df)
        df = df.dropna(subset=["order_id", "customer_id", "product_id", "sales", "profit"])
        self.raw_df = df
        self.orders = self._build_orders(df)
        self.customers = self._build_customers(df)
        self.products = self._build_products(df)
        self.source_path = path
        LOGGER.info("数据读取完成，共 %s 条记录，订单数 %s 个，客户数 %s 个。", len(df), self.orders.shape[0], self.customers.shape[0])

    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        统一列名，兼容不同数据源字段命名。

        :param df: 原始数据框。
        :return: 处理后的数据框。
        """
        rename_map: Dict[str, str] = {
            "Order ID": "order_id",
            "OrderID": "order_id",
            "订单编号": "order_id",
            "Customer ID": "customer_id",
            "客户编号": "customer_id",
            "Product ID": "product_id",
            "产品编号": "product_id",
            "Quantity": "quantity",
            "数量": "quantity",
            "Sales": "sales",
            "销售额": "sales",
            "Profit": "profit",
            "利润": "profit",
            "Discount": "discount",
            "折扣": "discount",
            "Order Date": "order_date",
            "订单日期": "order_date",
            "Product Name": "product_name",
            "产品名称": "product_name",
            "Category": "category",
            "类别": "category",
            "Sub-Category": "sub_category",
            "子类别": "sub_category",
        }
        df = df.rename(columns={col: rename_map.get(col, col) for col in df.columns})
        return df

    def _convert_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        处理字段类型并补充缺失值。

        :param df: 标准列名的数据框。
        :return: 类型转换后的数据框。
        """
        numeric_cols = ["quantity", "sales", "profit", "discount"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        if "order_date" in df.columns:
            df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
        df["discount"] = df.get("discount", 0).fillna(0)
        df["quantity"] = df.get("quantity", 1).fillna(1)
        df["sales"] = df["sales"].fillna(0)
        df["profit"] = df["profit"].fillna(0)
        return df

    def _build_orders(self, df: pd.DataFrame) -> pd.DataFrame:
        """按订单汇总基础信息。"""
        grouped = df.groupby("order_id").agg(
            customer_id=("customer_id", "first"),
            order_date=("order_date", "first"),
            sales=("sales", "sum"),
            profit=("profit", "sum"),
            discount=("discount", "mean"),
        )
        grouped = grouped.reset_index()
        return grouped

    def _build_customers(self, df: pd.DataFrame) -> pd.DataFrame:
        """按客户汇总消费情况。"""
        grouped = df.groupby("customer_id").agg(
            order_count=("order_id", "nunique"),
            total_sales=("sales", "sum"),
            total_profit=("profit", "sum"),
            first_order_date=("order_date", "min"),
            last_order_date=("order_date", "max"),
        )
        return grouped.reset_index()

    def _build_products(self, df: pd.DataFrame) -> pd.DataFrame:
        """按商品汇总销售指标。"""
        grouped = df.groupby(["product_id", "product_name"], dropna=False).agg(
            quantity=("quantity", "sum"),
            sales=("sales", "sum"),
            profit=("profit", "sum"),
            discount=("discount", "mean"),
        )
        grouped = grouped.reset_index()
        if grouped.empty:
            grouped["profit_rate"] = 0
        else:
            grouped["profit_rate"] = grouped.apply(lambda r: r["profit"] / r["sales"] if r["sales"] else 0, axis=1)
        return grouped

    def get_latest_date(self) -> Optional[datetime]:
        """返回数据集中最新订单日期。"""
        if self.raw_df is None or "order_date" not in self.raw_df:
            return None
        return self.raw_df["order_date"].max()

    def overview(self) -> Dict[str, object]:
        """返回数据概览，用于前端展示。"""
        if self.raw_df is None:
            raise ValueError("尚未加载任何数据集。")
        latest_date = self.get_latest_date()
        earliest = self.raw_df["order_date"].min() if "order_date" in self.raw_df else None
        return {
            "records": int(len(self.raw_df)),
            "orders": int(self.orders.shape[0]) if self.orders is not None else 0,
            "customers": int(self.customers.shape[0]) if self.customers is not None else 0,
            "products": int(self.products.shape[0]) if self.products is not None else 0,
            "start_date": earliest.strftime("%Y-%m-%d") if earliest is not None else None,
            "end_date": latest_date.strftime("%Y-%m-%d") if latest_date is not None else None,
            "source_path": self.source_path,
        }


data_repo = DataRepository()
