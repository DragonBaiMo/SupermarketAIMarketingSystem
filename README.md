# 超市 AI 营销系统（前后端分离版）

面向本科毕设的本地运行项目，后端使用 **Python + FastAPI** 提供营销分析 API，前端使用 **Vue3 + TypeScript + Vite** 进行可视化展示，覆盖客户推荐、促销分析、销售预测、客户聚类与语音播报等功能。

## 目录结构

```
backend/           # Python 后端（FastAPI 服务与算法模块）
frontend/          # Vue3 前端（TypeScript + Vite）
data/              # 默认 CSV 数据存放目录（自行放置 sales_data.csv）
outputs/           # 日志、导出与图表输出目录
schema.sql         # SQLite 表结构（可选持久化）
docs/defense.md    # 答辩材料
```

## 环境准备

1. 安装 Python 3.10+ 与 Node.js 18+。
2. 创建并激活虚拟环境后安装后端依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 安装前端依赖：
   ```bash
   cd frontend
   npm install
   ```

## 运行后端（FastAPI）

```bash
uvicorn backend.main:app --reload --port 8000
```

* 默认允许跨域，前端可直接访问 `http://localhost:8000/api`。
* 如果未指定路径，后端会尝试读取 `data/sales_data.csv`，可通过接口或前端页面上传。

## 运行前端（Vue3 + Vite）

```bash
cd frontend
npm run dev -- --host --port 5173
```

浏览器访问 `http://localhost:5173/#/`，侧边栏可进入各功能模块。

## 主要接口（/api）

- `POST /data/upload`：上传 CSV 并加载。
- `POST /data/load`：从指定路径加载 CSV。
- `GET /data/overview`：查看记录数、客户数、日期范围。
- `POST /recommend`：输入客户 ID 与 TopN 获取推荐商品。
- `POST /promotion`：按阈值筛选促销候选商品。
- `POST /promotion/analyze`：基于 Apriori 的购物篮关联规则挖掘。
- `POST /forecast`：按月预测未来销售额与利润。
- `POST /clustering`：基于 RFM 的 KMeans 聚类与分群解释。
- `POST /export`：导出推荐、促销、预测、分群的 CSV。
- `POST /tts`：播报任意文本（本地音频环境需可用）。
- `POST /tts/minimax` 与 `GET /tts/minimax/status/{task_id}`：调用 MiniMax 云端语音合成并轮询下载链接。

## 前端功能看板

- **数据管理**：上传/加载 CSV，显示基础数据概览。
- **客户推荐**：输入客户 ID，展示 TopN 推荐并支持 CSV 导出。
- **促销分析**：配置销量、利润率、折扣阈值，筛选候选商品并导出；可切换关联规则挖掘展示“啤酒+尿布”等组合建议，未命中规则时自动放宽阈值保障结果可见。
- **销售预测**：选择预测月份数，查看销售/利润折线图与摘要，支持导出；自动对比 ARIMA 与线性回归，先用补齐后的时间序列做留出验证，再择优展示更能刻画周期性的结果。
- **客户分群**：设置聚类数，查看分群柱状图与分群表，支持导出。
- **语音播报**：既可本地播放，也可提交 MiniMax 任务后轮询获取云端高质量音频链接。

## MiniMax 云端语音配置

- 设置环境变量 `MINIMAX_API_KEY` 与 `MINIMAX_GROUP_ID`，可选的默认发音人 `MINIMAX_VOICE_ID`。
- API 基地址默认为 `https://api.minimax.chat/v1`，后端接口会先提交任务再通过 `task_id` 查询状态与下载地址。

## 数据与持久化

- 默认读取 `data/sales_data.csv`，可通过上传接口替换。
- 提供 `schema.sql` 便于将清洗后数据落地到 SQLite（可选）。

## 自测建议

1. 启动后端与前端。
2. 在“数据与总览”页面上传 CSV 样例，确认概览数据刷新。
3. 依次验证推荐、促销、预测、聚类页面，查看图表与导出文件。
4. 如需语音播报，在有音频输出的本机环境调用 `/api/tts`。
