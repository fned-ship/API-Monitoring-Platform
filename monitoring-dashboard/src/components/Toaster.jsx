import { AlertTriangle, Sparkles, X } from "lucide-react";
import { SEVERITY_COLOR } from "../utils/format";

export default function Toaster({ toasts, onDismiss }) {
  return (
    <div className="pointer-events-none fixed right-6 top-6 z-50 flex w-80 flex-col gap-2">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`animate-slide-in pointer-events-auto rounded-lg border bg-panel-raised/95 px-4 py-3 shadow-2xl backdrop-blur ${
            SEVERITY_COLOR[toast.severity] || SEVERITY_COLOR.MEDIUM
          }`}
        >
          <div className="flex items-start gap-2.5">
            {toast.kind === "alert" ? (
              <AlertTriangle size={16} className="mt-0.5 shrink-0" />
            ) : (
              <Sparkles size={16} className="mt-0.5 shrink-0" />
            )}
            <div className="min-w-0 flex-1">
              <div className="text-[10px] uppercase tracking-[0.15em] opacity-80">
                {toast.kind === "alert" ? "Alert" : "AI prediction"} · {toast.serviceName}
              </div>
              <p className="mt-0.5 text-[13px] leading-snug text-ink-primary">{toast.message}</p>
            </div>
            <button
              onClick={() => onDismiss(toast.id)}
              className="shrink-0 text-ink-faint hover:text-ink-primary"
              aria-label="Dismiss notification"
            >
              <X size={14} />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
