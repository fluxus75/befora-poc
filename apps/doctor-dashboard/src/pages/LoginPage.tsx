import { FormEvent, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { useAuthStore } from '../stores/authStore';

export default function LoginPage() {
  const login = useAuthStore((state) => state.login);
  const user = useAuthStore((state) => state.user);
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    try {
      await login(username, password);
      navigate('/');
    } catch {
      setError('Invalid credentials. Try again.');
    }
  };

  useEffect(() => {
    if (user) {
      navigate('/');
    }
  }, [user, navigate]);
  if (user) {
    return null;
  }

  return (
    <div className="page center">
      <form className="card" onSubmit={handleSubmit} style={{ minWidth: 320 }}>
        <h2>Doctor Dashboard</h2>
        <p>Sign in with your assigned account.</p>
        <div className="grid">
          <input
            className="input"
            placeholder="Username"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
          />
          <input
            className="input"
            placeholder="Password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </div>
        {error ? <p style={{ color: 'var(--danger)' }}>{error}</p> : null}
        <button className="btn" type="submit" style={{ marginTop: 12 }}>
          Sign In
        </button>
      </form>
    </div>
  );
}
