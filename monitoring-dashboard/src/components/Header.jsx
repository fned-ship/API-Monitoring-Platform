import { Radio, ChevronDown } from "lucide-react";

export default function Header({ services, selectedService, onSelectService, connected }) {
  return (
    <header className="flex items-center justify-between border-b border-panel-line px-8 py-5">
      <div className="flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-md bg-panel-raised">
          <Radio size={16} className="text-forecast" strokeWidth={2.5} />
        </div>
        <div>
          <h1 className="font-display text-[15px] font-semibold tracking-tight text-ink-primary">
            API Monitoring Console
          </h1>
          <p className="text-[11px] text-ink-faint tracking-wide">
            live telemetry · predictive risk · alerts
          </p>
        </div>
      </div>

      <div className="flex items-center gap-5">
        <div className="relative">
          <select
            value={selectedService || ""}
            onChange={(e) => onSelectService(e.target.value)}
            className="appearance-none rounded-md border border-panel-line bg-panel-raised py-2 pl-3 pr-8 font-mono text-xs text-ink-primary outline-none focus:border-forecast/60"
          >
            {services.length === 0 && <option value="">no services yet</option>}
            {services.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
          <ChevronDown
            size={14}
            className="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 text-ink-faint"
          />
        </div>

        <div className="flex items-center gap-2 font-mono text-[11px] text-ink-muted">
          <span
            className={`h-1.5 w-1.5 rounded-full ${
              connected ? "bg-signal-calm" : "bg-signal-critical"
            }`}
          />
          {connected ? "LIVE" : "RECONNECTING"}
        </div>
      </div>
    </header>
  );
}
