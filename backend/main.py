"""FastAPI 版后端入口，提供前后端分离接口。"""
import os
from io import StringIO
from typing import Any, Dict, List

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from backend import config
from backend.api_models import (AssociationRule, ClusterRequest, ExportRequest,
                                ForecastRequest, LoadRequest,
                                MiniMaxTTSRequest, PromotionAnalyzeRequest,
                                PromotionRule, RecommendRequest)
from backend.data_loader import data_repo
from backend.modules import clustering, forecast, promotion, recommender
from backend.modules.tts import query_minimax_task, speak, submit_minimax_task
from backend.utils.logger import LOGGER, ensure_dirs

app = FastAPI(title="超市AI营销系统", description="提供营销分析 API，配合 Vue 前端使用")
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _ensure_data_loaded() -> None:
    """校验数据是否已加载。"""
    if data_repo.raw_df is None:
        raise HTTPException(status_code=400, detail="请先在数据管理中上传或加载销售 CSV 文件")


@app.on_event("startup")
def _prepare_environment() -> None:
    """启动时创建必要目录。"""
    ensure_dirs()
    os.makedirs(config.DATA_DIR, exist_ok=True)


@app.get("/api/health")
def health() -> Dict[str, str]:
    """健康检查。"""
    return {"status": "ok"}


@app.post("/api/data/load")
def load_data(req: LoadRequest) -> Dict[str, Any]:
    """从指定路径读取 CSV。"""
    path = req.path or config.DEFAULT_CSV
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"未找到数据文件：{path}")
    try:
        data_repo.load_csv(path)
    except Exception as exc:  # noqa: BLE001
        LOGGER.error("读取数据失败：%s", exc)
        raise HTTPException(status_code=400, detail="数据加载失败，请检查文件格式与编码") from exc
    return {"message": "加载完成", "overview": data_repo.overview()}


@app.post("/api/data/upload")
async def upload_data(file: UploadFile = File(...)) -> Dict[str, Any]:
    """上传 CSV 文件并立即加载。"""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="仅支持上传 CSV 文件")
    os.makedirs(config.DATA_DIR, exist_ok=True)
    target_path = os.path.join(config.DATA_DIR, file.filename)
    content = await file.read()
    with open(target_path, "wb") as f:
        f.write(content)
    try:
        data_repo.load_csv(target_path)
    except Exception as exc:  # noqa: BLE001
        LOGGER.error("上传后解析失败：%s", exc)
        raise HTTPException(status_code=400, detail="上传文件格式异常，请确认列名与编码") from exc
    return {"message": "上传并加载成功", "overview": data_repo.overview()}


@app.get("/api/data/overview")
def overview() -> Dict[str, Any]:
    """返回当前数据集的统计信息。"""
    _ensure_data_loaded()
    return data_repo.overview()


@app.post("/api/recommend")
def recommend(req: RecommendRequest) -> Dict[str, List[Dict[str, Any]]]:
    """客户个性化推荐。"""
    _ensure_data_loaded()
    rec = recommender.Recommender(data_repo)
    try:
        df = rec.recommend(req.customer_id, req.top_n)
    except Exception as exc:  # noqa: BLE001
        LOGGER.error("推荐计算失败：%s", exc)
        raise HTTPException(status_code=400, detail="推荐计算失败，请检查客户编号") from exc
    return {"items": df.to_dict(orient="records")}


@app.post("/api/promotion")
def promotion_candidates(rule: PromotionRule) -> Dict[str, Any]:
    """促销候选筛选。"""
    _ensure_data_loaded()
    metrics = promotion.calc_product_metrics(data_repo)
    result = promotion.select_promotion_candidates(metrics, rule.dict())
    return {"items": result.to_dict(orient="records"), "total": int(len(result))}


@app.post("/api/promotion/analyze")
def promotion_analyze(req: PromotionAnalyzeRequest) -> Dict[str, Any]:
    """使用 Apriori 进行购物篮关联分析。"""
    _ensure_data_loaded()
    try:
        rules: List[AssociationRule] = promotion.mine_association_rules(
            data_repo,
            min_support=req.min_support,
            min_confidence=req.min_confidence,
            metric=req.metric,
        )
    except Exception as exc:  # noqa: BLE001
        LOGGER.error("关联规则挖掘失败：%s", exc)
        raise HTTPException(status_code=400, detail="关联规则挖掘失败，请调整参数后重试") from exc
    return {"items": [rule.dict() for rule in rules], "total": len(rules)}


@app.post("/api/forecast")
def forecast_sales(req: ForecastRequest) -> Dict[str, Any]:
    """销售额与利润预测。"""
    _ensure_data_loaded()
    ts_df = forecast.build_sales_timeseries(data_repo)
    history, predict_df, model_info = forecast.train_and_predict_sales(ts_df, req.months)
    summary = forecast.summarize_forecast(predict_df, model_info)
    return {
        "history": history.to_dict(orient="records"),
        "forecast": predict_df.to_dict(orient="records"),
        "summary": summary,
        "model": model_info,
    }


@app.post("/api/clustering")
def cluster(req: ClusterRequest) -> Dict[str, Any]:
    """客户聚类分析。"""
    _ensure_data_loaded()
    rfm_df = clustering.calc_rfm(data_repo)
    cluster_df, _ = clustering.kmeans_cluster(rfm_df, req.k)
    summary = clustering.explain_clusters(cluster_df)
    return {
        "clusters": cluster_df.to_dict(orient="records"),
        "summary": summary.to_dict(orient="records"),
    }


@app.post("/api/export")
def export_data(req: ExportRequest) -> StreamingResponse:
    """根据类型导出 CSV。"""
    _ensure_data_loaded()
    target = req.target
    df = None
    if target == "recommendation":
        rec = recommender.Recommender(data_repo)
        df = rec.recommend(req.customer_id or "", req.top_n)
    elif target == "promotion":
        metrics = promotion.calc_product_metrics(data_repo)
        df = promotion.select_promotion_candidates(metrics, PromotionRule().dict())
    elif target == "cluster":
        rfm_df = clustering.calc_rfm(data_repo)
        cluster_df, _ = clustering.kmeans_cluster(rfm_df, req.k)
        df = cluster_df
    elif target == "forecast":
        ts_df = forecast.build_sales_timeseries(data_repo)
        _, predict_df, _ = forecast.train_and_predict_sales(ts_df, req.months)
        df = predict_df
    else:
        raise HTTPException(status_code=400, detail="不支持的导出类型")

    if df is None or df.empty:
        raise HTTPException(status_code=400, detail="暂无可导出的数据")
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
    csv_buffer.seek(0)
    filename = f"{target}.csv"
    headers = {"Content-Disposition": f"attachment; filename={filename}"}
    return StreamingResponse(iter([csv_buffer.getvalue()]), media_type="text/csv", headers=headers)


@app.post("/api/tts")
def tts(text: str) -> Dict[str, str]:
    """触发本地语音播报。"""
    if not text:
        raise HTTPException(status_code=400, detail="播报内容不能为空")
    try:
        speak(text)
    except Exception as exc:  # noqa: BLE001
        LOGGER.error("语音播报失败：%s", exc)
        raise HTTPException(status_code=500, detail="语音播报失败，请检查本地音频环境") from exc
    return {"message": "已开始播放"}


@app.post("/api/tts/minimax")
def minimax_tts(req: MiniMaxTTSRequest) -> Dict[str, str]:
    """提交 MiniMax 文本转语音任务。"""
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="播报内容不能为空")
    try:
        result = submit_minimax_task(req.text, req.voice_id)
    except Exception as exc:  # noqa: BLE001
        LOGGER.error("MiniMax 任务提交失败：%s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return result


@app.get("/api/tts/minimax/status/{task_id}")
def minimax_tts_status(task_id: str) -> Dict[str, str]:
    """查询 MiniMax 语音合成状态。"""
    if not task_id:
        raise HTTPException(status_code=400, detail="task_id 不能为空")
    try:
        result = query_minimax_task(task_id)
    except Exception as exc:  # noqa: BLE001
        LOGGER.error("查询 MiniMax 任务失败：%s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return result
