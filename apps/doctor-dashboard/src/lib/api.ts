import axios from 'axios';

import { useAuthStore } from '../stores/authStore';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '',
  withCredentials: true,
});

api.interceptors.request.use((config) => {
  const csrfToken = useAuthStore.getState().csrfToken;
  const method = config.method?.toLowerCase();
  if (csrfToken && method && ['post', 'patch', 'delete', 'put'].includes(method)) {
    config.headers = {
      ...config.headers,
      'X-CSRF-Token': csrfToken,
    };
  }
  return config;
});

export default api;
