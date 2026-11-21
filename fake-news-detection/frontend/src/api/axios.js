import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";

const api = axios.create({ baseURL: API_BASE_URL });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auto-refresh on 401 once, then bounce to login if that fails too.
let isRefreshing = false;

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry && !isRefreshing) {
      original._retry = true;
      isRefreshing = true;
      const refreshToken = localStorage.getItem("refresh_token");
      try {
        if (!refreshToken) throw new Error("No refresh token");
        const { data } = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
          refresh: refreshToken,
        });
        localStorage.setItem("access_token", data.access);
        original.headers.Authorization = `Bearer ${data.access}`;
        isRefreshing = false;
        return api(original);
      } catch (refreshError) {
        isRefreshing = false;
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/login";
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export default api;
