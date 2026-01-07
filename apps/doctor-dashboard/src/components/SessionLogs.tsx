import type { SessionLogEntry } from '../types';

interface SessionLogsProps {
  logs: SessionLogEntry[];
}

export default function SessionLogs({ logs }: SessionLogsProps) {
  return (
    <div className="card">
      <h3>Conversation Logs</h3>
      <div className="grid">
        {logs.length === 0 ? (
          <p>No logs yet.</p>
        ) : (
          logs.map((log) => (
            <div key={log.turn_index} className="card">
              <div className="session-meta">
                <span>Turn {log.turn_index}</span>
                <span>{new Date(log.timestamp).toLocaleString()}</span>
              </div>
              <p>
                <strong>User:</strong> {log.user_input ?? '-'}
              </p>
              <p>
                <strong>Agent:</strong> {log.agent_response ?? '-'}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
