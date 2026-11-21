import { Navigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

export function PrivateRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="main-content">Loading…</div>;
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

export function AdminRoute({ children }) {
  const { user, isAdmin, loading } = useAuth();
  if (loading) return <div className="main-content">Loading…</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (!isAdmin) return <Navigate to="/submit" replace />;
  return children;
}
