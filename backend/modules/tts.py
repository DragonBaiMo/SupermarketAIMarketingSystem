"""语音播报模块，支持本地 TTS 与 MiniMax 云端合成。"""
import os
import subprocess
import time
import uuid
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import urlparse

import pyttsx3
import requests

from backend import config
from backend.utils.logger import LOGGER, ensure_dirs

# 由于 aurastd 接口为同步返回，这里使用内存缓存模拟任务，以兼容前端轮询逻辑
_MINIMAX_TASK_CACHE: Dict[str, Dict[str, str]] = {}
_AUDIO_PLAYER_PROCESS: Optional[subprocess.Popen] = None
_LOCAL_TTS_ENGINE: Optional[pyttsx3.Engine] = None


def _get_tts_engine() -> pyttsx3.Engine:
    global _LOCAL_TTS_ENGINE
    if _LOCAL_TTS_ENGINE is None:
        _LOCAL_TTS_ENGINE = pyttsx3.init()
    return _LOCAL_TTS_ENGINE


def _stop_audio_process() -> None:
    global _AUDIO_PLAYER_PROCESS
    if _AUDIO_PLAYER_PROCESS and _AUDIO_PLAYER_PROCESS.poll() is None:
        try:
            _AUDIO_PLAYER_PROCESS.terminate()
            _AUDIO_PLAYER_PROCESS.wait(timeout=2)
        except Exception:
            try:
                _AUDIO_PLAYER_PROCESS.kill()
            except Exception:
                pass
    _AUDIO_PLAYER_PROCESS = None


def speak(text: str) -> None:
    """
    将文本转为语音播放。

    :param text: 需要播报的中文文本。
    """
    if not text:
        LOGGER.warning("没有可播报的内容。")
        return
    try:
        engine = _get_tts_engine()
        try:
            engine.stop()
        except Exception:
            pass
        engine.setProperty("rate", config.TTS_RATE)
        engine.setProperty("volume", config.TTS_VOLUME)
        LOGGER.info("开始语音播报：%s", text)
        engine.say(text)
        engine.runAndWait()
    except Exception as exc:  # noqa: BLE001
        LOGGER.error("语音播报失败，可手动朗读结果。错误：%s", exc)


def submit_minimax_task(text: str, voice_id: Optional[str] = None) -> Dict[str, str]:
    """调用 aurastd TTS，同步获取结果，落盘存档后写入缓存并尝试自动播报。"""
    _check_minimax_settings()
    ensure_dirs()
    payload: Dict[str, object] = {
        "text": text,
        "voice_setting": {
            "voice_id": voice_id or config.MINIMAX_DEFAULT_VOICE,
            "speed": 1,
            "vol": 1,
            "pitch": 0,
        },
        "audio_setting": {
            "sample_rate": 32000,
            "bitrate": 128000,
            "format": "mp3",
            "channel": 1,
        },
        "output_format": "url",
        "stream": False,
    }
    if config.MINIMAX_TTS_MODEL:
        payload["model"] = config.MINIMAX_TTS_MODEL

    headers = _build_headers()
    LOGGER.info("调用 aurastd 语音合成，请求载荷: %s", payload)
    resp = requests.post(
        f"{config.MINIMAX_API_BASE}/tts",
        headers=headers,
        json=payload,
        timeout=60,
        verify=False,
    )
    if resp.status_code >= 400:
        LOGGER.error("MiniMax 任务提交失败：%s", resp.text)
        raise RuntimeError("MiniMax 任务提交失败，请检查配置与网络。")
    data = resp.json()
    audio_value = data.get("audio")
    if not audio_value:
        LOGGER.error("MiniMax 返回缺少音频数据，原始响应：%s", data)
        raise RuntimeError("MiniMax 返回结果缺少音频链接或数据。")

    task_id = uuid.uuid4().hex
    status = data.get("status", "success")
    cache_value = {
        "status": "success" if str(status).lower() in {"ok", "success", "2"} else "processing",
        "audio_url": audio_value if _is_url(audio_value) else "",
        "audio_hex": "" if _is_url(audio_value) else audio_value,
        "local_path": "",
        "message": "语音生成成功",
    }
    if cache_value["status"] == "success":
        cache_value["local_path"] = _save_audio(task_id, cache_value["audio_url"], cache_value["audio_hex"])
        _try_play_audio(cache_value["local_path"])
    _MINIMAX_TASK_CACHE[task_id] = cache_value
    LOGGER.info("MiniMax 任务提交成功，task_id=%s", task_id)
    return {
        "task_id": task_id,
        "status": cache_value["status"],
        "audio_url": cache_value["audio_url"],
        "local_path": cache_value["local_path"],
        "message": "语音生成成功，可通过状态接口获取结果",
    }


def query_minimax_task(task_id: str) -> Dict[str, str]:
    """轮询 MiniMax 任务状态，返回音频地址等信息。"""
    _check_minimax_settings()
    if task_id not in _MINIMAX_TASK_CACHE:
        raise RuntimeError("未找到对应的语音任务，请确认 task_id 是否有效。")
    result = _MINIMAX_TASK_CACHE[task_id]
    LOGGER.info("MiniMax 任务状态：%s", result.get("status"))
    return {
        "status": result.get("status", "processing"),
        "audio_url": result.get("audio_url"),
        "audio_hex": result.get("audio_hex"),
        "local_path": result.get("local_path", ""),
        "message": result.get("message", ""),
    }


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


def _is_url(value: str) -> bool:
    """判断是否为有效链接。"""
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _save_audio(task_id: str, audio_url: str, audio_hex: str) -> str:
    """将云端返回的音频保存到本地，便于归档与离线播放。"""
    os.makedirs(config.TTS_AUDIO_DIR, exist_ok=True)
    target_path = Path(config.TTS_AUDIO_DIR) / f"{task_id}.mp3"
    try:
        if audio_url:
            resp = requests.get(audio_url, timeout=30, verify=False)
            resp.raise_for_status()
            target_path.write_bytes(resp.content)
        elif audio_hex:
            target_path.write_bytes(bytes.fromhex(audio_hex))
        else:
            LOGGER.warning("音频内容为空，未生成文件。")
            return ""
        LOGGER.info("已保存云端音频到本地：%s", target_path)
        return str(target_path)
    except Exception as exc:  # noqa: BLE001
        LOGGER.error("保存云端音频失败：%s", exc)
        return ""


def _try_play_audio(path_str: str) -> None:
    """尝试自动播放已保存的音频文件（优先静默方式）。"""
    if not path_str:
        return
    path = Path(path_str)
    if not path.exists():
        LOGGER.warning("未找到可播放的音频文件：%s", path)
        return
    try:
        _stop_audio_process()
        if os.name == "nt":
            # 使用隐藏窗口调用 MediaPlayer，避免弹窗影响体验
            cmd = [
                "powershell",
                "-NoProfile",
                "-WindowStyle",
                "Hidden",
                "-Command",
                (
                    "Add-Type -AssemblyName PresentationCore;"
                    "$player = New-Object System.Windows.Media.MediaPlayer;"
                    f"$player.Open('{path.as_posix()}');"
                    "$player.Volume = 1;"
                    "$player.Play();"
                    "Start-Sleep 10;"
                ),
            ]
            global _AUDIO_PLAYER_PROCESS
            _AUDIO_PLAYER_PROCESS = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            _AUDIO_PLAYER_PROCESS = subprocess.Popen(["xdg-open", str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        LOGGER.info("已自动播放音频：%s", path)
    except Exception as exc:  # noqa: BLE001
        LOGGER.warning("自动播放音频失败，请手动打开文件：%s，原因：%s", path, exc)
