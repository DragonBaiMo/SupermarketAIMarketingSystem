"""系统配置模块，集中管理路径与默认参数。"""
import os

# 基础目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)

# 加载项目根目录 .env 到环境变量（不覆盖已存在的同名变量）
def _load_env_file() -> None:
    env_path = os.path.join(PROJECT_DIR, ".env")
    if not os.path.exists(env_path):
        return
    try:
        with open(env_path, "r", encoding="utf-8") as file:
            for raw_line in file:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                if not key:
                    continue
                if value.startswith(("\"", "'")) and value.endswith(("\"", "'")):
                    value = value[1:-1]
                os.environ.setdefault(key, value)
    except Exception:
        # 忽略 .env 读取异常，避免阻断服务启动
        return


_load_env_file()

# 数据与输出目录
DATA_DIR = os.path.join(PROJECT_DIR, "data")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "outputs")

# 默认文件路径
DEFAULT_CSV = os.path.join(DATA_DIR, "sales_data.csv")
DEFAULT_EXPORT_DIR = os.path.join(OUTPUT_DIR, "exports")
DEFAULT_FIGURE_DIR = os.path.join(OUTPUT_DIR, "figures")
TTS_AUDIO_DIR = os.path.join(OUTPUT_DIR, "tts")

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
DEFAULT_MIN_SUPPORT = 0.01
DEFAULT_MIN_CONFIDENCE = 0.5

# 日志相关
LOG_LEVEL = "INFO"
LOG_FILE = os.path.join(OUTPUT_DIR, "system.log")

# 语音播报
TTS_RATE = 170
TTS_VOLUME = 1.0
MINIMAX_API_BASE = os.getenv("MINIMAX_API_BASE", "https://tts.aurastd.com/api/v1")
# 留空时不传递模型参数，使用服务端默认模型，避免因模型名称变更导致请求失败
MINIMAX_TTS_MODEL = os.getenv("MINIMAX_TTS_MODEL", "")
MINIMAX_DEFAULT_VOICE = os.getenv("MINIMAX_VOICE_ID", "Chinese (Mandarin)_Warm_Girl")
MINIMAX_GROUP_ID = os.getenv("MINIMAX_GROUP_ID", "")
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_POLL_INTERVAL = 2

# 前端跨域配置（本地调试与部署时务必限制来源域名）
# 生产环境请改为实际受信任的前端域名列表，避免使用 ["*"] 造成安全风险。
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]  # TODO: 部署时替换为正式前端域名
