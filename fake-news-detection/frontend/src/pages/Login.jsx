import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await login(form.username, form.password);
      navigate("/submit");
    } catch (err) {
      setError(err.response?.data?.non_field_errors?.[0] || "Invalid username or password.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="main-content auth-shell">
      <div className="card">
        <p className="eyebrow">Sign in</p>
        <h2>Welcome back</h2>
        {error && <div className="error-banner">{error}</div>}
        <form onSubmit={handleSubmit}>
          <label htmlFor="username">Username</label>
          <input
            id="username"
            value={form.username}
            onChange={(e) => setForm({ ...form, username: e.target.value })}
            required
          />
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            required
          />
          <button className="btn" type="submit" disabled={submitting}>
            {submitting ? "Signing in…" : "Sign in"}
          </button>
        </form>
        <p className="helper-text" style={{ marginTop: "1rem" }}>
          No account? <Link to="/register">Register here</Link>
        </p>
      </div>
    </div>
  );
}
