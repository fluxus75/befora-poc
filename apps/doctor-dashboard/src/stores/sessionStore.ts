import { create } from 'zustand';

import api from '../lib/api';
import type {
  SessionDetail,
  SessionListItem,
  SessionListResponse,
  SessionNote,
} from '../types';

interface SessionState {
  sessions: SessionListItem[];
  total: number;
  page: number;
  pageSize: number;
  detail: SessionDetail | null;
  loading: boolean;
  fetchSessions: (page?: number, status?: string) => Promise<void>;
  fetchSessionDetail: (sessionId: string) => Promise<void>;
  updateSlots: (sessionId: string, slots: Record<string, string | null>) => Promise<void>;
  addNote: (sessionId: string, note: string) => Promise<SessionNote>;
  updateStatus: (sessionId: string, status: string) => Promise<void>;
}

export const useSessionStore = create<SessionState>((set) => ({
  sessions: [],
  total: 0,
  page: 1,
  pageSize: 20,
  detail: null,
  loading: false,
  fetchSessions: async (page = 1, status) => {
    set({ loading: true });
    const response = await api.get<SessionListResponse>('/api/sessions', {
      params: { page, status },
    });
    set({
      sessions: response.data.items,
      total: response.data.total,
      page: response.data.page,
      pageSize: response.data.page_size,
      loading: false,
    });
  },
  fetchSessionDetail: async (sessionId) => {
    set({ loading: true });
    const response = await api.get<SessionDetail>(`/api/sessions/${sessionId}`);
    set({ detail: response.data, loading: false });
  },
  updateSlots: async (sessionId, slots) => {
    const payload = {
      slots: Object.entries(slots).map(([slot_key, slot_value]) => ({
        slot_key,
        slot_value,
      })),
    };
    const response = await api.patch<SessionDetail>(
      `/api/sessions/${sessionId}/slots`,
      payload
    );
    set({ detail: response.data });
  },
  addNote: async (sessionId, note) => {
    const response = await api.post<SessionNote>(
      `/api/sessions/${sessionId}/notes`,
      { note }
    );
    set((state) =>
      state.detail
        ? {
            detail: { ...state.detail, notes: [response.data, ...state.detail.notes] },
          }
        : state
    );
    return response.data;
  },
  updateStatus: async (sessionId, status) => {
    const response = await api.patch<SessionDetail>(
      `/api/sessions/${sessionId}/status`,
      { status }
    );
    set({ detail: response.data });
  },
}));
