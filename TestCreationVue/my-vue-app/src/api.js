// src/api.js
import axios from "axios";
import jwtDecode from "jwt-decode"; // Run: npm install jwt-decode

const api = axios.create({
  baseURL: "http://127.0.0.1:5000", // Change to your teammate’s IP if needed
});

// Buffer before expiration to trigger refresh
const REFRESH_BUFFER_SECONDS = 30;

// Request interceptor to add token and refresh if needed
api.interceptors.request.use(async (config) => {
  const token = localStorage.getItem("token");

  if (token) {
    try {
      const decoded = jwtDecode(token);
      const currentTime = Math.floor(Date.now() / 1000);

      // If token is close to expiring, try refreshing it
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
}, (error) => Promise.reject(error));

// Refresh token function (calls backend route)
async function refreshToken() {
  const currentToken = localStorage.getItem("token");
  if (!currentToken) return null;

  try {
    const res = await axios.post("http://127.0.0.1:5000/auth/refresh", {
      token: currentToken
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
