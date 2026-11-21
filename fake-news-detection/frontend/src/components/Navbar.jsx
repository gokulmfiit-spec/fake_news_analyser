import { Link, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout, isAdmin } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const isActive = (path) => (location.pathname === path ? "active" : "");

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <header className="masthead">
      <div className="masthead-brand">
        VerifyNews <small>Fake News Verification Desk</small>
      </div>
      <nav className="masthead-nav">
        {user ? (
          <>
            <Link className={isActive("/submit")} to="/submit">Submit</Link>
            <Link className={isActive("/history")} to="/history">History</Link>
            <Link className={isActive("/analytics")} to="/analytics">Analytics</Link>
            {isAdmin && <Link className={isActive("/admin")} to="/admin">Admin</Link>}
            <span className="helper-text">{user.username}</span>
            <button onClick={handleLogout}>Log out</button>
          </>
        ) : (
          <>
            <Link className={isActive("/login")} to="/login">Log in</Link>
            <Link className={isActive("/register")} to="/register">Register</Link>
          </>
        )}
      </nav>
    </header>
  );
}
