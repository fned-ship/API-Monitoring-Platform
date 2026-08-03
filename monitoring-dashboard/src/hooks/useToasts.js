import { useCallback, useRef, useState } from "react";

const AUTO_DISMISS_MS = 8000;
const MAX_VISIBLE = 4;

export function useToasts() {
  const [toasts, setToasts] = useState([]);
  const idRef = useRef(0);

  const push = useCallback((toast) => {
    const id = ++idRef.current;
    setToasts((prev) => [{ ...toast, id }, ...prev].slice(0, MAX_VISIBLE));
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, AUTO_DISMISS_MS);
  }, []);

  const dismiss = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return { toasts, push, dismiss };
}
