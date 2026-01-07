import { FormEvent, useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';

import ReportViewer from '../components/ReportViewer';
import SessionLogs from '../components/SessionLogs';
import SlotEditor from '../components/SlotEditor';
import { useAuthStore } from '../stores/authStore';
import { useSessionStore } from '../stores/sessionStore';

export default function SessionDetailPage() {
  const { sessionId } = useParams();
  const fetchSessionDetail = useSessionStore((state) => state.fetchSessionDetail);
  const updateSlots = useSessionStore((state) => state.updateSlots);
  const addNote = useSessionStore((state) => state.addNote);
  const updateStatus = useSessionStore((state) => state.updateStatus);
  const detail = useSessionStore((state) => state.detail);
  const loading = useSessionStore((state) => state.loading);
  const user = useAuthStore((state) => state.user);
  const [note, setNote] = useState('');

  useEffect(() => {
    if (sessionId) {
      void fetchSessionDetail(sessionId);
    }
  }, [fetchSessionDetail, sessionId]);

  if (!sessionId) {
    return (
      <div className="page layout">
        <p>Invalid session.</p>
      </div>
    );
  }

  if (loading || !detail) {
    return (
      <div className="page layout">
        <p>Loading session...</p>
      </div>
    );
  }

  const readOnly = user?.role === 'reviewer';

  const handleSaveSlots = async (slots: Record<string, string | null>) => {
    await updateSlots(sessionId, slots);
  };

  const handleNoteSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!note.trim()) {
      return;
    }
    await addNote(sessionId, note.trim());
    setNote('');
  };

  return (
    <div className="page layout grid">
      <Link to="/">← Back to sessions</Link>
      <div className="card">
        <h2>Session {detail.session_id}</h2>
        <div className="session-meta">
          <span className="badge">{detail.status}</span>
          <span>Patient ID: {detail.patient_id ?? 'N/A'}</span>
          <span>Assigned: {detail.assigned_doctor_id ?? 'Unassigned'}</span>
        </div>
        <div className="session-meta">
          <span>Created: {new Date(detail.created_at).toLocaleString()}</span>
          {detail.completed_at ? (
            <span>Completed: {new Date(detail.completed_at).toLocaleString()}</span>
          ) : null}
        </div>
        <div style={{ marginTop: 16, display: 'flex', gap: 8 }}>
          {user?.role === 'doctor' && detail.status !== 'reviewed' && detail.status !== 'confirmed' ? (
            <button className="btn" type="button" onClick={() => updateStatus(sessionId, 'reviewed')}>
              Mark Reviewed
            </button>
          ) : null}
          {user?.role === 'doctor' && detail.status === 'reviewed' ? (
            <button className="btn" type="button" onClick={() => updateStatus(sessionId, 'confirmed')}>
              Confirm
            </button>
          ) : null}
        </div>
      </div>
      <div className="grid two">
        <SlotEditor slots={detail.slots} readOnly={readOnly} onSave={handleSaveSlots} />
        <div className="grid">
          <div className="card">
            <h3>Doctor Notes</h3>
            {detail.notes.length === 0 ? <p>No notes.</p> : null}
            <ul>
              {detail.notes.map((item) => (
                <li key={item.id}>
                  {item.note} ({item.doctor_id})
                </li>
              ))}
            </ul>
            {readOnly ? null : (
              <form onSubmit={handleNoteSubmit} className="grid">
                <textarea
                  className="textarea"
                  rows={3}
                  value={note}
                  onChange={(event) => setNote(event.target.value)}
                  placeholder="Add a note"
                />
                <button className="btn" type="submit">
                  Add Note
                </button>
              </form>
            )}
          </div>
          <ReportViewer sessionId={detail.session_id} />
        </div>
      </div>
      <SessionLogs logs={detail.logs} />
    </div>
  );
}
