import http from "./http";

export const requestCloudSpeech = async (text: string): Promise<void> => {
  if (!text.trim()) {
    return;
  }
  try {
    await http.post("/tts/minimax", { text });
  } catch (error) {
    console.warn("云端语音播报失败：", error);
  }
};
