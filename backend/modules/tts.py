"""语音播报模块，支持本地 TTS 与 MiniMax 云端合成。"""
import time
from typing import Dict, Optional

import pyttsx3
import requests

from backend import config
from backend.utils.logger import LOGGER


def speak(text: str) -> None:
    """
    将文本转为语音播放。

    :param text: 需要播报的中文文本。
    """
    if not text:
        LOGGER.warning("没有可播报的内容。")
        return
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", config.TTS_RATE)
        engine.setProperty("volume", config.TTS_VOLUME)
        LOGGER.info("开始语音播报：%s", text)
        engine.say(text)
        engine.runAndWait()
    except Exception as exc:  # noqa: BLE001
        LOGGER.error("语音播报失败，可手动朗读结果。错误：%s", exc)


def submit_minimax_task(text: str, voice_id: Optional[str] = None) -> Dict[str, str]:
    """调用 MiniMax 异步接口提交语音合成任务。"""
    _check_minimax_settings()
    payload = {
        "model": config.MINIMAX_TTS_MODEL,
        "text": text,
        "voice_id": voice_id or config.MINIMAX_DEFAULT_VOICE,
        "audio_type": "mp3",
        "sample_rate": 24000,
    }
    headers = _build_headers()
    params = {"GroupId": config.MINIMAX_GROUP_ID} if config.MINIMAX_GROUP_ID else None
    resp = requests.post(
        f"{config.MINIMAX_API_BASE}/text_to_speech",
        headers=headers,
        params=params,
        json=payload,
        timeout=30,
    )
    if resp.status_code >= 400:
        LOGGER.error("MiniMax 任务提交失败：%s", resp.text)
        raise RuntimeError("MiniMax 任务提交失败，请检查配置与网络。")
    data = resp.json()
    task_id = data.get("task_id") or data.get("id")
    if not task_id:
        raise RuntimeError("MiniMax 返回结果缺少 task_id。")
    LOGGER.info("MiniMax 任务提交成功，task_id=%s", task_id)
    return {"task_id": task_id, "status": data.get("status", "processing"), "message": "语音生成任务已提交，请轮询状态"}


def query_minimax_task(task_id: str) -> Dict[str, str]:
    """轮询 MiniMax 任务状态，返回音频地址等信息。"""
    _check_minimax_settings()
    headers = _build_headers()
    params = {"GroupId": config.MINIMAX_GROUP_ID} if config.MINIMAX_GROUP_ID else None
    url = f"{config.MINIMAX_API_BASE}/text_to_speech/{task_id}"
    resp = requests.get(url, headers=headers, params=params, timeout=15)
    if resp.status_code >= 400:
        LOGGER.error("MiniMax 任务查询失败：%s", resp.text)
        raise RuntimeError("MiniMax 任务查询失败，请确认 task_id 是否有效。")
    data = resp.json()
    status = data.get("status", "processing")
    result = {
        "status": status,
        "audio_url": data.get("download_url"),
        "expiration": data.get("expiration", 0),
    }
    LOGGER.info("MiniMax 任务状态：%s", status)
    return result


def wait_and_download(task_id: str, timeout_seconds: int = 60) -> Optional[str]:
    """简单轮询等待任务完成，返回音频下载地址。"""
    start = time.time()
    while time.time() - start < timeout_seconds:
        result = query_minimax_task(task_id)
        if result["status"] == "success" and result.get("audio_url"):
            return result["audio_url"]
        time.sleep(config.MINIMAX_POLL_INTERVAL)
    LOGGER.warning("MiniMax 任务超时未完成，task_id=%s", task_id)
    return None


def _build_headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {config.MINIMAX_API_KEY}",
        "Content-Type": "application/json",
    }


def _check_minimax_settings() -> None:
    if not config.MINIMAX_API_KEY:
        raise RuntimeError("未配置 MINIMAX_API_KEY 环境变量，无法调用云端语音合成。")
