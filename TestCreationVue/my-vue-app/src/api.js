// src/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:5000',
  responseType: 'json'
});

// Attach the token to every outgoing request
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, error => Promise.reject(error));

// Response interceptor to handle token expiration and refresh
api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;

    // If request failed due to 401 and hasn't been retried
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const newToken = await refreshToken();

      if (newToken) {
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return api(originalRequest); // retry the original request with new token
      } else {
        console.warn("Token refresh failed or user logged out.");
      }
    }

    return Promise.reject(error);
  }
);

// Refresh token logic (calls backend /auth/refresh)
async function refreshToken() {
  const currentToken = localStorage.getItem('token');
  if (!currentToken) return null;

  try {
    const res = await axios.post('http://127.0.0.1:5000/auth/refresh', {
      token: currentToken
    });

    const newToken = res.data.token;
    localStorage.setItem('token', newToken);
    return newToken;
  } catch (err) {
    console.error('Token refresh failed:', err);
    localStorage.removeItem('token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('role');
    return null;
  }
}

export default api;
