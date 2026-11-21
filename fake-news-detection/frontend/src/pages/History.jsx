import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import api from "../api/axios";
import VerdictBadge from "../components/VerdictBadge";

export default function History() {
  const [results, setResults] = useState([]);
  const [search, setSearch] = useState("");
  const [label, setLabel] = useState("");
  const [loading, setLoading] = useState(true);

  const fetchHistory = async () => {
    setLoading(true);
    const params = {};
    if (search) params.search = search;
    if (label) params.label = label;
    const { data } = await api.get("/submissions/history/", { params });
    setResults(data.results || data);
    setLoading(false);
  };

  useEffect(() => {
    fetchHistory();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleFilter = (e) => {
    e.preventDefault();
    fetchHistory();
  };

  return (
    <div className="main-content">
      <p className="eyebrow">Your records</p>
      <h2>Submission history</h2>

      <form className="card" onSubmit={handleFilter} style={{ display: "flex", gap: "1rem", flexWrap: "wrap", alignItems: "flex-end" }}>
        <div style={{ flex: 2, minWidth: "220px" }}>
          <label htmlFor="search">Search</label>
          <input id="search" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search title or content…" />
        </div>
        <div style={{ flex: 1, minWidth: "160px" }}>
          <label htmlFor="label">Verdict</label>
          <select id="label" value={label} onChange={(e) => setLabel(e.target.value)}>
            <option value="">All</option>
            <option value="real">Likely Genuine</option>
            <option value="fake">Likely Fake</option>
            <option value="uncertain">Uncertain</option>
          </select>
        </div>
        <button className="btn" type="submit" style={{ marginBottom: "1rem" }}>Filter</button>
      </form>

      {loading ? (
        <p className="helper-text">Loading…</p>
      ) : results.length === 0 ? (
        <p className="helper-text">No submissions yet — try analyzing something first.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Title</th><th>Type</th><th>Verdict</th><th>Confidence</th><th>Submitted</th>
            </tr>
          </thead>
          <tbody>
            {results.map((r) => (
              <tr key={r.id}>
                <td>
                  {r.report_id ? (
                    <Link to={`/reports/${r.report_id}`}>{r.title || r.source_url || "Untitled"}</Link>
                  ) : (
                    r.title || r.source_url || "Untitled"
                  )}
                </td>
                <td>{r.submission_type}</td>
                <td>{r.label ? <VerdictBadge label={r.label} /> : "—"}</td>
                <td>{r.confidence_score != null ? `${Math.round(r.confidence_score * 100)}%` : "—"}</td>
                <td>{new Date(r.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
