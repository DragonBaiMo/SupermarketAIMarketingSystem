# 答辩材料包

## 系统简介

超市 AI 营销系统采用 **前后端分离** 架构：后端 FastAPI 负责数据清洗、推荐、促销、预测、聚类与语音播报；前端 Vue3 + TypeScript 提供数据管理与可视化展示，支持 CSV 上传、参数配置、图表查看与结果导出，满足本科毕设演示需求。

## 架构图（ASCII）
```
+------------------------+        +---------------------------+
|      Vue3 前端         | <----> |  FastAPI 后端(分析API)    |
| 数据管理/推荐/促销/预测/聚类 |        | 数据加载/算法/导出/TTS      |
+-----------+------------+        +-----------+---------------+
            |                                 |
            v                                 v
     浏览器交互与可视化                   pandas 数据视图
                                          (orders/customers/products)
```

## 流程图（IPO 主流程）
```
[上传或加载CSV]
       |
       v
[构建订单/客户/商品视图]
       |
       v
[前端按场景调用 API]
   |- 推荐: customer_id -> 推荐列表/导出/播报
   |- 促销: 规则阈值 -> 候选商品/导出
   |- 预测: 预测月数 -> 历史+预测曲线/导出
   |- 聚类: K 值 -> 分群表/可视化/导出
```

## 数据库结构图（SQLite 可选）
```
dim_customer(customer_id PK, customer_name, segment, city, province, country, region)
dim_product(product_id PK, category, sub_category, product_name)
fact_order(order_id PK, order_date, ship_date, ship_mode, customer_id FK, region)
fact_order_item(line_id PK, order_id FK, product_id FK, sales, quantity, discount, profit)
dm_customer_rfm(customer_id PK, recency, frequency, monetary, cluster_label)
dm_sales_summary(period PK, sales, profit)
```

## 技术亮点
- FastAPI + Pandas + scikit-learn 实现推荐/促销/预测/聚类的轻量可运行链路。
- Vue3 + ECharts 展示销售趋势与分群柱状图，支持在线参数调整与 CSV 导出。
- 数据加载兼容上传与本地路径，统一中文异常提示与日志，便于答辩演示。
- 导出接口覆盖推荐、促销、预测、聚类，前后端保持一致的数据口径。
- 语音播报使用本地 pyttsx3，演示时可直接播报核心结论。

## 开发总结
- 严格按照 PDR/PRD/IPO Must/Should 列表实现功能并提供可视化展示。
- 采用前后端分离目录，便于独立部署和调试；配置、阈值均可在前端实时调整。
- 代码全中文注释与提示，日志分级记录关键步骤，便于快速排错与讲解。
- 预留 schema.sql 方便落地 SQLite，满足数据持久化与扩展需求。
