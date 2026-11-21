import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import api from "../api/axios";
import ConfidenceMeter from "../components/ConfidenceMeter";
import VerdictBadge from "../components/VerdictBadge";

export default function ReportDetail() {
  const { id } = useParams();
  const [report, setReport] = useState(null);
  const [error, setError] = useState("");
  const [feedbackSent, setFeedbackSent] = useState(false);
  const [feedbackError, setFeedbackError] = useState("");

  useEffect(() => {
    let cancelled = false;
    api
      .get(`/reports/${id}/`)
      .then(({ data }) => {
        if (!cancelled) setReport(data);
      })
      .catch(() => {
        if (!cancelled) setError("Could not load this report.");
      });
    return () => {
      cancelled = true;
    };
  }, [id]);

  const sendFeedback = async (isHelpful) => {
    setFeedbackError("");
    try {
      await api.post("/feedback/", { report: report.id, is_helpful: isHelpful });
      setFeedbackSent(true);
    } catch {
      setFeedbackError("Could not submit feedback (you may have already rated this report).");
    }
  };

  if (error) return <div className="main-content"><div className="error-banner">{error}</div></div>;
  if (!report) return <div className="main-content">Loading report…</div>;

  const { submission, label, confidence_score, flagged_statements, summary, supporting_sources, credibility_score } = report;

  return (
    <div className="main-content">
      <p className="eyebrow">Fact Verification Report #{report.id}</p>
      <h2>{submission.title || "Untitled submission"}</h2>

      <div className="card">
        <div className="card-title-row">
          <VerdictBadge label={label} />
          <span className="helper-text">
            {new Date(report.created_at).toLocaleString()}
          </span>
        </div>
        <ConfidenceMeter score={confidence_score} label={label} />

        {credibility_score !== null && credibility_score !== undefined && (
          <p className="helper-text" style={{ marginTop: "0.8rem" }}>
            Source credibility score: <strong>{Math.round(credibility_score * 100)}%</strong>
            {submission.source_url && (
              <> — <a href={submission.source_url} target="_blank" rel="noreferrer">{submission.source_url}</a></>
            )}
          </p>
        )}
      </div>

      <div className="card">
        <p className="eyebrow">Verification summary</p>
        <p>{summary}</p>
      </div>

      <div className="card">
        <p className="eyebrow">Flagged / suspicious statements</p>
        {flagged_statements?.length ? (
          <ul className="flagged-list">
            {flagged_statements.map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>
        ) : (
          <p className="helper-text">No specific statements were flagged.</p>
        )}
      </div>

      {supporting_sources?.length > 0 && (
        <div className="card">
          <p className="eyebrow">Related coverage from trusted sources</p>
          <table>
            <thead>
              <tr><th>Title</th><th>Source</th><th>Published</th></tr>
            </thead>
            <tbody>
              {supporting_sources.map((s, i) => (
                <tr key={i}>
                  <td><a href={s.url} target="_blank" rel="noreferrer">{s.title}</a></td>
                  <td>{s.source}</td>
                  <td>{s.published_at ? new Date(s.published_at).toLocaleDateString() : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="card">
        <p className="eyebrow">Was this verification helpful?</p>
        {feedbackSent ? (
          <p className="helper-text">Thanks — your feedback has been recorded.</p>
        ) : (
          <>
            <div style={{ display: "flex", gap: "0.6rem" }}>
              <button className="btn secondary" onClick={() => sendFeedback(true)}>👍 Helpful</button>
              <button className="btn secondary" onClick={() => sendFeedback(false)}>👎 Not helpful</button>
            </div>
            {feedbackError && <p className="error-banner" style={{ marginTop: "0.8rem" }}>{feedbackError}</p>}
          </>
        )}
      </div>

      <div className="card">
        <p className="eyebrow">Submitted content</p>
        <p style={{ whiteSpace: "pre-wrap" }}>{submission.raw_content}</p>
      </div>
    </div>
  );
}
