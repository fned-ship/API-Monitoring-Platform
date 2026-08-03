import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";
import { formatTime } from "../utils/format";

function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-md border border-panel-line bg-panel-raised px-3 py-2 font-mono text-[11px] shadow-lg">
      <div className="text-ink-faint">{formatTime(label)}</div>
      {payload.map((p) => (
        <div key={p.dataKey} style={{ color: p.color }}>
          {p.name}: {p.value != null ? `${Math.round(p.value)}ms` : "—"}
        </div>
      ))}
    </div>
  );
}

// Plots actual response time as a solid line and the AI's forecast as a dashed
// periwinkle line offset into the future — the point of this panel is letting
// you visually see whether the dashed line leads the solid one.
export default function LatencyChart({ data }) {
  console.log(data);
  return (
    <div className="rounded-lg border border-panel-line bg-panel p-5">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-[11px] tracking-[0.15em] text-ink-faint uppercase">
          Response time — actual vs. forecast
        </h3>
        <div className="flex items-center gap-4 text-[11px] font-mono text-ink-muted">
          <span className="flex items-center gap-1.5">
            <span className="h-0.5 w-3 bg-ink-primary" /> actual
          </span>
          <span className="flex items-center gap-1.5">
            <span className="h-0.5 w-3 border-t border-dashed border-forecast" /> forecast
          </span>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={220}>
        <ComposedChart data={data} margin={{ top: 4, right: 8, left: -16, bottom: 0 }}>
          <CartesianGrid stroke="#1A222D" vertical={false} />
          <XAxis
            dataKey="time"
            tickFormatter={formatTime}
            stroke="#4B5866"
            tick={{ fontSize: 10, fontFamily: "JetBrains Mono" }}
            tickLine={false}
          />
          <YAxis
            stroke="#4B5866"
            tick={{ fontSize: 10, fontFamily: "JetBrains Mono" }}
            tickLine={false}
            width={44}
          />
          <Tooltip content={<ChartTooltip />} />
          <Line
            type="monotone"
            dataKey="actual"
            name="actual"
            stroke="#E7EDF3"
            strokeWidth={1.75}
            dot={false}
            isAnimationActive={false}
            connectNulls
          />
          <Line
            type="monotone"
            dataKey="forecast"
            name="forecast"
            stroke="#6C8EF5"
            strokeWidth={1.75}
            strokeDasharray="5 4"
            dot={false}
            isAnimationActive={false}
            connectNulls
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
