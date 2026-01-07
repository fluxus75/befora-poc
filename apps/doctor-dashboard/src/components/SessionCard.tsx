import { Link } from 'react-router-dom';

import type { SessionListItem } from '../types';

interface SessionCardProps {
  session: SessionListItem;
}

export default function SessionCard({ session }: SessionCardProps) {
  return (
    <Link to={`/sessions/${session.session_id}`} className="card session-card fade-in">
      <div className="session-meta">
        <span className="badge">{session.status}</span>
        <span>Session: {session.session_id}</span>
      </div>
      <div className="session-meta">
        <span>Created: {new Date(session.created_at).toLocaleString()}</span>
        {session.completed_at ? (
          <span>Completed: {new Date(session.completed_at).toLocaleString()}</span>
        ) : null}
      </div>
      <div className="session-meta">
        <span>Assigned doctor: {session.assigned_doctor_id ?? 'Unassigned'}</span>
      </div>
    </Link>
  );
}
