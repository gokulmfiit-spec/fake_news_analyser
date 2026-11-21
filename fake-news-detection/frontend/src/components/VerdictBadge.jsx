const LABELS = {
  real: "Likely Genuine",
  fake: "Likely Fake",
  uncertain: "Uncertain",
};

export default function VerdictBadge({ label }) {
  if (!label) return null;
  return <span className={`verdict-badge verdict-${label}`}>{LABELS[label] || label}</span>;
}
