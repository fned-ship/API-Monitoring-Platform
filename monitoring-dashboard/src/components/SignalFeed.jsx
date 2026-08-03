import { AlertTriangle, Sparkles } from "lucide-react";
import { formatTime, SEVERITY_DOT } from "../utils/format";

function FeedRow({ item }) {
  const isAlert = item.kind === "alert";
  const severity = item.severity || "MEDIUM";
  const dot = SEVERITY_DOT[severity] || "bg-signal-watch";

  return (
    <div className="animate-fade-up flex gap-3 border-b border-panel-line/60 px-1 py-3 last:border-0">
      <div className="flex flex-col items-center pt-1">
        <span className={`h-2 w-2 rounded-full ${dot}`} />
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2 text-[11px] font-mono text-ink-faint">
          <span>{formatTime(item.timestamp)}</span>
          <span className="text-ink-faint">·</span>
          {isAlert ? (
            <AlertTriangle size={11} className="text-signal-critical" />
          ) : (
            <Sparkles size={11} className="text-forecast" />
          )}
          <span className="uppercase tracking-wider">{isAlert ? "alert" : "prediction"}</span>
        </div>
        <p className="mt-0.5 truncate text-[13px] text-ink-primary">{item.message}</p>
        {item.detail && <p className="mt-0.5 text-[11px] text-ink-muted">{item.detail}</p>}
      </div>
    </div>
  );
}

export default function SignalFeed({ items }) {
  return (
    <div className="flex h-full flex-col rounded-lg border border-panel-line bg-panel">
      <div className="border-b border-panel-line px-5 py-4">
        <h3 className="text-[11px] tracking-[0.15em] text-ink-faint uppercase">Signal feed</h3>
        <p className="mt-0.5 text-[11px] text-ink-faint">alerts + AI predictions, most recent first</p>
      </div>
      <div className="flex-1 overflow-y-auto px-4">
        {items.length === 0 ? (
          <div className="flex h-full items-center justify-center px-6 text-center text-xs text-ink-faint">
            Nothing flagged yet. This is where alerts and AI risk predictions will appear the moment they fire.
          </div>
        ) : (
          items.map((item) => <FeedRow key={item.id} item={item} />)
        )}
      </div>
    </div>
  );
}
