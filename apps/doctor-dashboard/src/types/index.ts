export type Role = 'admin' | 'doctor' | 'reviewer';

export interface User {
  id: string;
  username: string;
  role: Role;
}

export interface SessionListItem {
  session_id: string;
  status: string;
  created_at: string;
  completed_at?: string | null;
  assigned_doctor_id?: string | null;
  reviewed_at?: string | null;
  confirmed_at?: string | null;
}

export interface SessionSlot {
  slot_key: string;
  slot_value?: string | null;
}

export interface SessionLogEntry {
  turn_index: number;
  user_input?: string | null;
  agent_response?: string | null;
  timestamp: string;
}

export interface SessionNote {
  id: number;
  doctor_id: string;
  note: string;
  created_at: string;
}

export interface SessionDetail extends SessionListItem {
  patient_id?: string | null;
  slots: SessionSlot[];
  logs: SessionLogEntry[];
  notes: SessionNote[];
}

export interface SessionListResponse {
  items: SessionListItem[];
  total: number;
  page: number;
  page_size: number;
}
