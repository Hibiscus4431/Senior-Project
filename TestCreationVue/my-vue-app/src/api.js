// src/api.js
import axios from "axios";
import jwt_decode from "jwt-decode"; // ✅ Correct import

const api = axios.create({
  baseURL: "http://127.0.0.1:5000",
});

const REFRESH_BUFFER_SECONDS = 30;

api.interceptors.request.use(
  async (config) => {
    const token = localStorage.getItem("token");

    if (token) {
      try {
        const decoded = jwt_decode(token); // ✅ Updated usage
        const currentTime = Math.floor(Date.now() / 1000);

        if (decoded.exp - currentTime < REFRESH_BUFFER_SECONDS) {
          const refreshed = await refreshToken();
          if (refreshed) {
            config.headers.Authorization = `Bearer ${refreshed}`;
          }
        } else {
          config.headers.Authorization = `Bearer ${token}`;
        }
      } catch (err) {
        console.warn("JWT decode failed", err);
      }
    }

    return config;
  },
  (error) => Promise.reject(error)
);

async function refreshToken() {
  const currentToken = localStorage.getItem("token");
  if (!currentToken) return null;

  try {
    const res = await axios.post("http://127.0.0.1:5000/auth/refresh", {
      token: currentToken,
    });

    const newToken = res.data.token;
    localStorage.setItem("token", newToken);
    return newToken;
  } catch (err) {
    console.error("Token refresh failed:", err);
    localStorage.removeItem("token");
    localStorage.removeItem("user_id");
    localStorage.removeItem("role");
    return null;
  }
}

export default api;
