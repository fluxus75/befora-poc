import { useEffect, useState } from 'react';

import SessionCard from '../components/SessionCard';
import { useSessionStore } from '../stores/sessionStore';

const STATUS_OPTIONS = [
  '',
  'active',
  'completed',
  'emergency_terminated',
  'reviewed',
  'confirmed',
];

export default function SessionListPage() {
  const [statusFilter, setStatusFilter] = useState('');
  const fetchSessions = useSessionStore((state) => state.fetchSessions);
  const sessions = useSessionStore((state) => state.sessions);
  const total = useSessionStore((state) => state.total);
  const page = useSessionStore((state) => state.page);
  const pageSize = useSessionStore((state) => state.pageSize);
  const loading = useSessionStore((state) => state.loading);

  useEffect(() => {
    void fetchSessions(1, statusFilter || undefined);
  }, [fetchSessions, statusFilter]);

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <div className="page layout">
      <div className="grid two">
        <div className="card">
          <h2>Session Overview</h2>
          <p>Browse completed intakes and review slot data.</p>
        </div>
        <div className="card">
          <label htmlFor="status-filter">Status filter</label>
          <select
            id="status-filter"
            className="select"
            value={statusFilter}
            onChange={(event) => setStatusFilter(event.target.value)}
          >
            {STATUS_OPTIONS.map((status) => (
              <option key={status} value={status}>
                {status || 'all'}
              </option>
            ))}
          </select>
        </div>
      </div>
      <div className="grid two" style={{ marginTop: 24 }}>
        {loading ? <p>Loading sessions...</p> : null}
        {sessions.map((session) => (
          <SessionCard key={session.session_id} session={session} />
        ))}
      </div>
      <div style={{ marginTop: 24, display: 'flex', gap: 12 }}>
        <button
          className="btn secondary"
          type="button"
          onClick={() => fetchSessions(Math.max(1, page - 1), statusFilter || undefined)}
          disabled={page <= 1}
        >
          Previous
        </button>
        <span>
          Page {page} / {totalPages}
        </span>
        <button
          className="btn secondary"
          type="button"
          onClick={() => fetchSessions(Math.min(totalPages, page + 1), statusFilter || undefined)}
          disabled={page >= totalPages}
        >
          Next
        </button>
      </div>
    </div>
  );
}
