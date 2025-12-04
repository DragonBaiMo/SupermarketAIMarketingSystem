"""系统配置模块，集中管理路径与默认参数。"""
import os

# 基础目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)

# 数据与输出目录
DATA_DIR = os.path.join(PROJECT_DIR, "data")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "outputs")

# 默认文件路径
DEFAULT_CSV = os.path.join(DATA_DIR, "sales_data.csv")
DEFAULT_EXPORT_DIR = os.path.join(OUTPUT_DIR, "exports")
DEFAULT_FIGURE_DIR = os.path.join(OUTPUT_DIR, "figures")

# 分析默认参数
DEFAULT_TOP_N = 5
DEFAULT_PROMOTION_RULE = {
    "min_quantity": 50,
    "max_quantity": 1000,
    "min_profit_rate": 0.05,
    "max_discount": 0.5,
}
DEFAULT_FORECAST_MONTHS = 3
DEFAULT_CLUSTER_K = 4

# 日志相关
LOG_LEVEL = "INFO"
LOG_FILE = os.path.join(OUTPUT_DIR, "system.log")

# 语音播报
TTS_RATE = 170
TTS_VOLUME = 1.0

# 前端跨域配置
ALLOWED_ORIGINS = ["*"]
