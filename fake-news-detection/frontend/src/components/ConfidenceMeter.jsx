const COLOR_BY_LABEL = {
  real: "var(--verified)",
  fake: "var(--fake)",
  uncertain: "var(--uncertain)",
};

export default function ConfidenceMeter({ score, label }) {
  const pct = Math.round((score || 0) * 100);
  return (
    <div>
      <div className="confidence-meter">
        <div
          className="confidence-meter-fill"
          style={{ width: `${pct}%`, background: COLOR_BY_LABEL[label] || "var(--accent)" }}
        />
      </div>
      <span className="helper-text">{pct}% confidence</span>
    </div>
  );
}
