export function formatTime(iso) {
  if (!iso) return "--:--:--";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "--:--:--";
  return d.toLocaleTimeString("en-GB", { hour12: false });
}

export function formatMs(value) {
  if (value === undefined || value === null) return "—";
  return `${Math.round(value)}ms`;
}

export function formatPct(value, digits = 1) {
  if (value === undefined || value === null) return "—";
  return `${(value * 100).toFixed(digits)}%`;
}

export const SEVERITY_COLOR = {
  LOW: "text-signal-calm border-signal-calm/40",
  MEDIUM: "text-signal-watch border-signal-watch/40",
  HIGH: "text-signal-critical border-signal-critical/40",
  CRITICAL: "text-signal-critical border-signal-critical/40",
};

export const SEVERITY_DOT = {
  LOW: "bg-signal-calm",
  MEDIUM: "bg-signal-watch",
  HIGH: "bg-signal-critical",
  CRITICAL: "bg-signal-critical",
};

export function severityFromRisk(riskScore) {
  if (riskScore >= 0.75) return "HIGH";
  if (riskScore >= 0.4) return "MEDIUM";
  return "LOW";
}

export function trendGlyph(direction) {
  if (direction === "RISING") return "▲";
  if (direction === "FALLING") return "▼";
  return "▬";
}

export function trendColor(direction, metricIsBadWhenRising = true) {
  if (direction === "STABLE") return "text-ink-muted";
  const rising = direction === "RISING";
  const bad = metricIsBadWhenRising ? rising : !rising;
  return bad ? "text-signal-critical" : "text-signal-calm";
}
