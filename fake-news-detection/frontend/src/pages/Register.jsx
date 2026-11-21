import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await register(form);
      navigate("/submit");
    } catch (err) {
      const data = err.response?.data;
      const firstError = data && Object.values(data)[0];
      setError(Array.isArray(firstError) ? firstError[0] : "Registration failed. Try a different username.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="main-content auth-shell">
      <div className="card">
        <p className="eyebrow">Create account</p>
        <h2>Join VerifyNews</h2>
        {error && <div className="error-banner">{error}</div>}
        <form onSubmit={handleSubmit}>
          <label htmlFor="username">Username</label>
          <input
            id="username"
            value={form.username}
            onChange={(e) => setForm({ ...form, username: e.target.value })}
            required
          />
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
          />
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            minLength={8}
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            required
          />
          <button className="btn" type="submit" disabled={submitting}>
            {submitting ? "Creating account…" : "Create account"}
          </button>
        </form>
        <p className="helper-text" style={{ marginTop: "1rem" }}>
          Already registered? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
