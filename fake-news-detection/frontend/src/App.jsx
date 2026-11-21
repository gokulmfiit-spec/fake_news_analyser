import { Navigate, Route, Routes } from "react-router-dom";

import Navbar from "./components/Navbar";
import { AdminRoute, PrivateRoute } from "./components/PrivateRoute";
import { useAuth } from "./context/AuthContext";
import AdminDashboard from "./pages/AdminDashboard";
import Analytics from "./pages/Analytics";
import History from "./pages/History";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ReportDetail from "./pages/ReportDetail";
import Submit from "./pages/Submit";

export default function App() {
  const { user, loading } = useAuth();

  return (
    <div className="app-shell">
      <Navbar />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/submit"
          element={
            <PrivateRoute>
              <Submit />
            </PrivateRoute>
          }
        />
        <Route
          path="/reports/:id"
          element={
            <PrivateRoute>
              <ReportDetail />
            </PrivateRoute>
          }
        />
        <Route
          path="/history"
          element={
            <PrivateRoute>
              <History />
            </PrivateRoute>
          }
        />
        <Route
          path="/analytics"
          element={
            <PrivateRoute>
              <Analytics />
            </PrivateRoute>
          }
        />
        <Route
          path="/admin"
          element={
            <AdminRoute>
              <AdminDashboard />
            </AdminRoute>
          }
        />
        <Route
          path="/"
          element={
            loading ? (
              <div className="main-content">Loading…</div>
            ) : (
              <Navigate to={user ? "/submit" : "/login"} replace />
            )
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <footer className="footer-note">VerifyNews — AI-assisted fake news verification desk</footer>
    </div>
  );
}
