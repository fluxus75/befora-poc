interface ReportViewerProps {
  sessionId: string;
}

export default function ReportViewer({ sessionId }: ReportViewerProps) {
  return (
    <div className="card">
      <h3>Report</h3>
      <p>Generate a printable summary for this session.</p>
      <a
        className="btn"
        href={`/api/sessions/${sessionId}/report/html`}
        target="_blank"
        rel="noreferrer"
      >
        Open HTML Report
      </a>
    </div>
  );
}
