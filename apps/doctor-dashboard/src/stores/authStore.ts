import { create } from 'zustand';

import api from '../lib/api';
import type { User } from '../types';

interface LoginResponse {
  user: User;
  csrf_token: string;
}

interface AuthState {
  user: User | null;
  csrfToken: string | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  fetchMe: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  csrfToken: null,
  loading: true,
  login: async (username, password) => {
    const response = await api.post<LoginResponse>('/api/auth/login', {
      username,
      password,
    });
    sessionStorage.setItem('dashboard_csrf', response.data.csrf_token);
    set({ user: response.data.user, csrfToken: response.data.csrf_token });
  },
  logout: async () => {
    await api.post('/api/auth/logout');
    sessionStorage.removeItem('dashboard_csrf');
    set({ user: null, csrfToken: null });
  },
  fetchMe: async () => {
    set({ loading: true });
    try {
      const response = await api.get<User>('/api/auth/me');
      const csrfToken = sessionStorage.getItem('dashboard_csrf');
      set({ user: response.data, csrfToken, loading: false });
    } catch {
      set({ user: null, csrfToken: null, loading: false });
    }
  },
}));
