import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import api from "../api/axios";

const LABEL_COLORS = { real: "#2F6F4F", fake: "#B5433B", uncertain: "#B08328" };

export default function Analytics() {
  const [data, setData] = useState(null);

  useEffect(() => {
    api.get("/analytics/overview/").then(({ data }) => setData(data));
  }, []);

  if (!data) return <div className="main-content">Loading analytics…</div>;

  const pieData = data.label_breakdown.map((d) => ({ name: d.label, value: d.count }));
  const typeData = data.submission_type_breakdown.map((d) => ({ name: d.submission_type, count: d.count }));
  const trendData = data.daily_trend.map((d) => ({ day: d.day, count: d.count }));

  return (
    <div className="main-content">
      <p className="eyebrow">{data.scope === "platform" ? "Platform-wide" : "Your"} statistics</p>
      <h2>Reports & analytics dashboard</h2>

      <div className="stat-grid">
        <div className="stat-box"><div className="value">{data.total_submissions}</div><div className="label">Submissions</div></div>
        <div className="stat-box"><div className="value">{data.total_reports}</div><div className="label">Reports generated</div></div>
        <div className="stat-box"><div className="value">{data.average_confidence != null ? `${Math.round(data.average_confidence * 100)}%` : "—"}</div><div className="label">Avg. confidence</div></div>
        <div className="stat-box"><div className="value">{data.feedback_helpful_ratio != null ? `${Math.round(data.feedback_helpful_ratio * 100)}%` : "—"}</div><div className="label">Feedback: helpful</div></div>
      </div>

      <div className="card">
        <p className="eyebrow">Verdict breakdown</p>
        {pieData.length ? (
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={pieData} dataKey="value" nameKey="name" outerRadius={90} label>
                {pieData.map((entry) => (
                  <Cell key={entry.name} fill={LABEL_COLORS[entry.name] || "#999"} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        ) : (
          <p className="helper-text">No reports yet.</p>
        )}
      </div>

      <div className="card">
        <p className="eyebrow">Submissions over time</p>
        {trendData.length ? (
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={trendData}>
              <CartesianGrid stroke="#D8D3C7" strokeDasharray="3 3" />
              <XAxis dataKey="day" tick={{ fontSize: 11 }} />
              <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Line type="monotone" dataKey="count" stroke="#2A4B7C" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p className="helper-text">No trend data yet.</p>
        )}
      </div>

      <div className="card">
        <p className="eyebrow">Submissions by type</p>
        {typeData.length ? (
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={typeData}>
              <CartesianGrid stroke="#D8D3C7" strokeDasharray="3 3" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="count" fill="#2A4B7C" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p className="helper-text">No submissions yet.</p>
        )}
      </div>
    </div>
  );
}
