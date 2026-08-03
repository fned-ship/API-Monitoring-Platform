import { severityFromRisk } from "../utils/format";

const COLORS = {
  LOW: "#3DDC97",
  MEDIUM: "#F2B84B",
  HIGH: "#F2545B",
};

const LABELS = {
  LOW: "NOMINAL",
  MEDIUM: "ELEVATED",
  HIGH: "AT RISK",
};

// The page's signature element: a circular risk gauge that breathes when the
// classification model's risk score climbs, giving one glance the whole point
// of the AI service — "is this about to become a problem."
export default function RiskPulse({ riskScore = 0, modelVersion, hasModel }) {
  const severity = severityFromRisk(riskScore);
  const color = COLORS[severity];
  const label = LABELS[severity];

  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const clamped = Math.max(0, Math.min(1, riskScore));
  const dashOffset = circumference * (1 - clamped);
  const pulse = severity !== "LOW";

  return (
    <div className="relative flex flex-col items-center justify-center py-6">
      <div className="relative h-44 w-44">
        {pulse && (
          <div
            className="absolute inset-0 rounded-full animate-pulse-ring"
            style={{ backgroundColor: color, filter: "blur(18px)" }}
          />
        )}
        <svg viewBox="0 0 160 160" className="relative h-44 w-44 -rotate-90">
          <circle
            cx="80" cy="80" r={radius}
            fill="none" stroke="#1A222D" strokeWidth="10"
          />
          {Array.from({ length: 40 }).map((_, i) => {
            const angle = (i / 40) * 360;
            return (
              <line
                key={i}
                x1="80" y1="6" x2="80" y2="12"
                stroke="#232C38"
                strokeWidth="1.5"
                transform={`rotate(${angle} 80 80)`}
              />
            );
          })}
          <circle
            cx="80" cy="80" r={radius}
            fill="none"
            stroke={color}
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={dashOffset}
            style={{ transition: "stroke-dashoffset 0.6s ease, stroke 0.4s ease" }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          {hasModel ? (
            <>
              <span className="font-mono text-4xl font-semibold tabular-nums" style={{ color }}>
                {Math.round(clamped * 100)}
              </span>
              <span className="mt-0.5 text-[10px] tracking-[0.2em] text-ink-muted">RISK SCORE</span>
            </>
          ) : (
            <span className="text-[11px] tracking-[0.15em] text-ink-faint px-6 text-center leading-relaxed">
              NO MODEL
              <br />TRAINED YET
            </span>
          )}
        </div>
      </div>
      {hasModel && (
        <>
          <div
            className="mt-4 rounded-full border px-3 py-1 font-mono text-xs tracking-[0.2em]"
            style={{ color, borderColor: `${color}66` }}
          >
            {label}
          </div>
          {modelVersion && (
            <div className="mt-2 text-[11px] text-ink-faint font-mono">model {modelVersion}</div>
          )}
        </>
      )}
    </div>
  );
}
