"""语音播报模块。"""
import pyttsx3

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
