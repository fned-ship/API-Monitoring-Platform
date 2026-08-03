import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { trendColor } from "../utils/format";

// target_metric's VALUE is always the Python feature-column name (snake_case) —
// only JSON object KEYS get converted to camelCase by the backend fix, not this string value.
const METRIC_LABELS = {
  avg_response_time_ms: "Latency",
  error_ratio_5xx: "Error rate",
  avg_cpu_usage_pct: "CPU usage",
};

const TREND_ICON = { RISING: TrendingUp, FALLING: TrendingDown, STABLE: Minus };

function formatValue(metric, value) {
  if (value == null) return "—";
  if (metric?.toLowerCase().includes("cpu")) return `${value.toFixed(1)}%`;
  if (metric?.toLowerCase().includes("error")) return `${(value * 100).toFixed(1)}%`;
  return `${Math.round(value)}ms`;
}

export default function ForecastCards({ forecasts }) {
  const entries = Object.values(forecasts || {});

  if (entries.length === 0) {
    return (
      <div className="rounded-lg border border-panel-line bg-panel p-5 text-center text-xs text-ink-faint">
        No forecasts yet — waiting on a trained regression model.
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
      {entries.map((f) => {
        const Icon = TREND_ICON[f.trendDirection] || Minus;
        const isCpuOrError = /cpu|error/i.test(f.targetMetric || "");
        const color = trendColor(f.trendDirection, !isCpuOrError ? true : true);
        const label = METRIC_LABELS[f.targetMetric] || f.targetMetric;

        return (
          <div key={f.targetMetric} className="rounded-lg border border-panel-line bg-panel p-4">
            <div className="flex items-center justify-between">
              <span className="text-[10px] tracking-[0.15em] text-ink-faint uppercase">{label}</span>
              <Icon size={14} className={color} />
            </div>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="font-mono text-lg font-semibold text-ink-primary">
                {formatValue(f.targetMetric, f.predictedValue)}
              </span>
              <span className="text-[11px] text-ink-faint font-mono">
                now {formatValue(f.targetMetric, f.currentValue)}
              </span>
            </div>
            <div className={`mt-1 font-mono text-[11px] ${color}`}>
              {f.predictedChangePct != null
                ? `${f.predictedChangePct >= 0 ? "+" : ""}${(f.predictedChangePct * 100).toFixed(1)}%`
                : "—"}{" "}
              in {Math.round((f.horizonSeconds || 300) / 60)}m
            </div>
          </div>
        );
      })}
    </div>
  );
}
