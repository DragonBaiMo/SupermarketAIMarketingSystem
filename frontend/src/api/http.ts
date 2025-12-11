import axios from "axios";

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || "http://localhost:8000/api",
  timeout: 15000
});

http.interceptors.response.use(
  (resp) => resp,
  (error) => {
    const msg = error?.response?.data?.detail || "请求失败，请稍后重试";
    return Promise.reject(new Error(msg));
  }
);

export default http;
