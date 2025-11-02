import axios from "axios";

// Prefer Vite env, fallback to localhost for dev
const API_BASE_URL = import.meta?.env?.VITE_API_URL || "http://127.0.0.1:8000/api";

export const api = axios.create({
  baseURL: API_BASE_URL,
});

// Get token from localStorage
export function getAuthHeaders() {
  const token = localStorage.getItem("access_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

// Attach Authorization header automatically
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token && !config.headers?.Authorization) {
    config.headers = { ...(config.headers || {}), Authorization: `Bearer ${token}` };
  }
  return config;
});

// Attempt token refresh on 401 once
let isRefreshing = false;
let pendingRequests = [];

function onRefreshed(newToken) {
  pendingRequests.forEach((cb) => cb(newToken));
  pendingRequests = [];
}

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    const status = error?.response?.status;
    if (status === 401 && !original._retry) {
      original._retry = true;
      const refresh = localStorage.getItem("refresh_token");
      if (!refresh) return Promise.reject(error);

      if (isRefreshing) {
        return new Promise((resolve) => {
          pendingRequests.push((token) => {
            original.headers = { ...(original.headers || {}), Authorization: `Bearer ${token}` };
            resolve(api(original));
          });
        });
      }

      isRefreshing = true;
      try {
        const resp = await api.post("/accounts/token/refresh/", { refresh });
        const newAccess = resp?.data?.access;
        const newRefresh = resp?.data?.refresh; // when rotation is enabled
        if (newAccess) localStorage.setItem("access_token", newAccess);
        if (newRefresh) localStorage.setItem("refresh_token", newRefresh);
        isRefreshing = false;
        onRefreshed(newAccess);
        original.headers = { ...(original.headers || {}), Authorization: `Bearer ${newAccess}` };
        return api(original);
      } catch (e) {
        isRefreshing = false;
        pendingRequests = [];
        // optional: clear tokens here
        return Promise.reject(error);
      }
    }
    return Promise.reject(error);
  }
);
