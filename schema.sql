-- 超市 AI 营销系统 SQLite 结构定义
PRAGMA foreign_keys = ON;

-- 原始订单明细
CREATE TABLE IF NOT EXISTS order_items (
    order_id TEXT NOT NULL,
    customer_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    product_name TEXT,
    quantity INTEGER DEFAULT 1,
    sales REAL DEFAULT 0,
    profit REAL DEFAULT 0,
    discount REAL DEFAULT 0,
    order_date TEXT,
    PRIMARY KEY (order_id, product_id)
);

-- 订单汇总
CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    order_date TEXT,
    sales REAL,
    profit REAL,
    discount REAL
);

-- 客户指标
CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    order_count INTEGER,
    total_sales REAL,
    total_profit REAL,
    first_order_date TEXT,
    last_order_date TEXT
);

-- 商品指标
CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    product_name TEXT,
    quantity INTEGER,
    sales REAL,
    profit REAL,
    discount REAL,
    profit_rate REAL
);

-- 按月聚合的销售与利润
CREATE TABLE IF NOT EXISTS monthly_sales (
    period TEXT PRIMARY KEY,
    sales REAL,
    profit REAL
);

-- 客户 RFM 与聚类标签
CREATE TABLE IF NOT EXISTS customer_clusters (
    customer_id TEXT PRIMARY KEY,
    R REAL,
    F REAL,
    M REAL,
    cluster INTEGER,
    label TEXT
);
