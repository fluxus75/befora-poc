import { useNavigate } from 'react-router-dom';

import { useAuthStore } from '../stores/authStore';

export default function Header() {
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <header className="header">
      <div className="header-inner">
        <div>
          <strong>Befora Doctor Dashboard</strong>
        </div>
        <div className="session-meta">
          <span>{user?.username}</span>
          <span className="badge">{user?.role}</span>
          <button className="btn secondary" type="button" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}
