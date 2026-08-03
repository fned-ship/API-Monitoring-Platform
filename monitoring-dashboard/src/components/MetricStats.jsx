import { formatMs, formatPct } from "../utils/format";

function StatCard({ label, value, unit, accent }) {
  return (
    <div className="rounded-lg border border-panel-line bg-panel px-5 py-4">
      <div className="text-[10px] tracking-[0.15em] text-ink-faint uppercase">{label}</div>
      <div className="mt-1.5 flex items-baseline gap-1.5">
        <span
          className="font-mono text-2xl font-semibold tabular-nums"
          style={{ color: accent || "#E7EDF3" }}
        >
          {value}
        </span>
        {unit && <span className="text-xs text-ink-muted">{unit}</span>}
      </div>
    </div>
  );
}

export default function MetricStats({ requestCount, avgLatencyMs, errorRatio }) {
  const errorAccent = errorRatio > 0.05 ? "#F2545B" : "#3DDC97";
  const latencyAccent = avgLatencyMs > 1000 ? "#F2545B" : avgLatencyMs > 500 ? "#F2B84B" : "#3DDC97";

  return (
    <div className="grid grid-cols-3 gap-3">
      <StatCard label="Requests (recent)" value={requestCount ?? "—"} />
      <StatCard label="Avg latency" value={formatMs(avgLatencyMs).replace("ms", "")} unit="ms" accent={latencyAccent} />
      <StatCard label="Error ratio" value={formatPct(errorRatio ?? 0)} accent={errorAccent} />
    </div>
  );
}
