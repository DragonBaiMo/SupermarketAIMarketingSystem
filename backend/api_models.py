"""FastAPI 请求与响应数据模型。"""
from typing import List, Optional

from pydantic import BaseModel, Field

from backend import config


class LoadRequest(BaseModel):
    """数据加载请求。"""

    path: Optional[str] = Field(None, description="CSV 文件路径，不填使用默认样例路径")


class PromotionRule(BaseModel):
    """促销筛选规则。"""

    min_quantity: float = Field(config.DEFAULT_PROMOTION_RULE["min_quantity"], description="最低销量")
    max_quantity: float = Field(config.DEFAULT_PROMOTION_RULE["max_quantity"], description="最高销量")
    min_profit_rate: float = Field(config.DEFAULT_PROMOTION_RULE["min_profit_rate"], description="最低利润率")
    max_discount: float = Field(config.DEFAULT_PROMOTION_RULE["max_discount"], description="最高折扣")


class PromotionAnalyzeRequest(BaseModel):
    """关联规则挖掘参数。"""

    min_support: float = Field(config.DEFAULT_MIN_SUPPORT, description="最小支持度")
    min_confidence: float = Field(config.DEFAULT_MIN_CONFIDENCE, description="最小置信度")
    metric: str = Field("lift", description="规则排序指标")


class AssociationRule(BaseModel):
    """用于返回前端的关联规则。"""

    antecedents: List[str]
    consequents: List[str]
    support: float
    confidence: float
    lift: float
    reason: str


class RecommendRequest(BaseModel):
    """客户推荐请求。"""

    customer_id: str = Field(..., description="客户编号")
    top_n: int = Field(config.DEFAULT_TOP_N, description="推荐数量")


class ForecastRequest(BaseModel):
    """销售预测请求。"""

    months: int = Field(config.DEFAULT_FORECAST_MONTHS, description="预测月份数")


class ClusterRequest(BaseModel):
    """聚类参数请求。"""

    k: int = Field(config.DEFAULT_CLUSTER_K, description="聚类数量")


class ExportRequest(BaseModel):
    """导出任务请求。"""

    target: str = Field(..., description="导出类型，支持 recommendation/promotion/cluster/forecast")
    customer_id: Optional[str] = Field(None, description="当导出推荐时需要客户 ID")
    top_n: int = Field(config.DEFAULT_TOP_N, description="导出推荐的数量")
    months: int = Field(config.DEFAULT_FORECAST_MONTHS, description="预测导出的月份数")
    k: int = Field(config.DEFAULT_CLUSTER_K, description="聚类导出的群组数量")


class MiniMaxTTSRequest(BaseModel):
    """MiniMax 文本转语音请求。"""

    text: str = Field(..., min_length=1, description="需要合成的中文文本")
    voice_id: Optional[str] = Field(None, description="自定义发音人标识，不填使用默认值")
