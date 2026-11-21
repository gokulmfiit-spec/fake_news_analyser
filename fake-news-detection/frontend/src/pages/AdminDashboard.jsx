import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import api from "../api/axios";
import VerdictBadge from "../components/VerdictBadge";

export default function AdminDashboard() {
  const [summary, setSummary] = useState(null);
  const [users, setUsers] = useState([]);
  const [reports, setReports] = useState([]);
  const [tab, setTab] = useState("overview");

  useEffect(() => {
    api.get("/admin-panel/summary/").then(({ data }) => setSummary(data));
    api.get("/admin-panel/users/").then(({ data }) => setUsers(data.results || data));
    api.get("/admin-panel/reports/").then(({ data }) => setReports(data.results || data));
  }, []);

  const toggleRole = async (user) => {
    const newRole = user.role === "admin" ? "user" : "admin";
    await api.patch(`/admin-panel/users/${user.id}/`, { role: newRole });
    setUsers((prev) => prev.map((u) => (u.id === user.id ? { ...u, role: newRole } : u)));
  };

  return (
    <div className="main-content">
      <p className="eyebrow">Administration</p>
      <h2>Admin dashboard</h2>

      <div className="stat-grid">
        <div className="stat-box"><div className="value">{summary?.total_users ?? "—"}</div><div className="label">Users</div></div>
        <div className="stat-box"><div className="value">{summary?.total_submissions ?? "—"}</div><div className="label">Submissions</div></div>
        <div className="stat-box"><div className="value">{summary?.fake_flagged ?? "—"}</div><div className="label">Flagged fake</div></div>
        <div className="stat-box"><div className="value">{summary?.real_flagged ?? "—"}</div><div className="label">Flagged genuine</div></div>
      </div>

      <div className="tabs">
        <button className={tab === "overview" ? "active" : ""} onClick={() => setTab("overview")}>Recent reports</button>
        <button className={tab === "users" ? "active" : ""} onClick={() => setTab("users")}>User management</button>
      </div>

      {tab === "overview" ? (
        <div className="card">
          <table>
            <thead><tr><th>Title</th><th>User</th><th>Verdict</th><th>Confidence</th><th>Date</th></tr></thead>
            <tbody>
              {reports.map((r) => (
                <tr key={r.id}>
                  <td><Link to={`/reports/${r.id}`}>{r.submission?.title || r.submission?.source_url || "Untitled"}</Link></td>
                  <td>{r.submission?.user?.username || "—"}</td>
                  <td><VerdictBadge label={r.label} /></td>
                  <td>{Math.round(r.confidence_score * 100)}%</td>
                  <td>{new Date(r.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="card">
          <table>
            <thead><tr><th>Username</th><th>Email</th><th>Role</th><th>Joined</th><th></th></tr></thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td>{u.username}</td>
                  <td>{u.email}</td>
                  <td>{u.role}</td>
                  <td>{new Date(u.created_at).toLocaleDateString()}</td>
                  <td><button className="btn secondary" onClick={() => toggleRole(u)}>
                    {u.role === "admin" ? "Revoke admin" : "Make admin"}
                  </button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
