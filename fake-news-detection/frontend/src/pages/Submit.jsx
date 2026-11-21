import { useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../api/axios";

export default function Submit() {
  const navigate = useNavigate();
  const [mode, setMode] = useState("text"); // 'text' | 'url'
  const [textForm, setTextForm] = useState({ submission_type: "text", title: "", raw_content: "" });
  const [url, setUrl] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const submitText = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const { data } = await api.post("/submissions/text/", textForm);
      navigate(`/reports/${data.id}`);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not analyze this content. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const submitUrl = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const { data } = await api.post("/submissions/url/", { source_url: url });
      navigate(`/reports/${data.id}`);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not fetch or analyze this URL.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="main-content">
      <p className="eyebrow">Verification Desk</p>
      <h2>Submit content for verification</h2>
      <p className="helper-text" style={{ marginBottom: "1.4rem" }}>
        Paste a news article, headline, or social media post, or hand over a URL — the AI engine
        will assess it for signs of misinformation and return a confidence-scored verdict.
      </p>

      <div className="tabs">
        <button className={mode === "text" ? "active" : ""} onClick={() => setMode("text")}>
          Article / Headline / Post
        </button>
        <button className={mode === "url" ? "active" : ""} onClick={() => setMode("url")}>
          URL Verification
        </button>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {mode === "text" ? (
        <form className="card" onSubmit={submitText}>
          <label htmlFor="submission_type">Content type</label>
          <select
            id="submission_type"
            value={textForm.submission_type}
            onChange={(e) => setTextForm({ ...textForm, submission_type: e.target.value })}
          >
            <option value="text">News Article</option>
            <option value="headline">Headline</option>
            <option value="social_post">Social Media Post</option>
          </select>

          <label htmlFor="title">Title (optional)</label>
          <input
            id="title"
            value={textForm.title}
            onChange={(e) => setTextForm({ ...textForm, title: e.target.value })}
            placeholder="e.g. Headline or short description"
          />

          <label htmlFor="raw_content">Content</label>
          <textarea
            id="raw_content"
            required
            value={textForm.raw_content}
            onChange={(e) => setTextForm({ ...textForm, raw_content: e.target.value })}
            placeholder="Paste the full article text, headline, or post here…"
          />

          <button className="btn" type="submit" disabled={submitting}>
            {submitting ? "Analyzing…" : "Analyze content"}
          </button>
        </form>
      ) : (
        <form className="card" onSubmit={submitUrl}>
          <label htmlFor="url">Article URL</label>
          <input
            id="url"
            type="url"
            required
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com/news/article"
          />
          <p className="helper-text" style={{ marginBottom: "1rem" }}>
            We'll fetch the page, extract the article text, and run it through the same
            verification pipeline plus a source-credibility check on the domain.
          </p>
          <button className="btn" type="submit" disabled={submitting}>
            {submitting ? "Fetching & analyzing…" : "Fetch & analyze"}
          </button>
        </form>
      )}
    </div>
  );
}
