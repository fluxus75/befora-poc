import { Link } from 'react-router-dom';

export default function NotFoundPage() {
  return (
    <div className="page layout">
      <h2>Page not found</h2>
      <Link to="/">Go back home</Link>
    </div>
  );
}
