import { useEffect, useRef, useState } from "react";
import SockJS from "sockjs-client";
import { Client } from "@stomp/stompjs";

const WS_URL = import.meta.env.VITE_DASHBOARD_WS_URL || "http://localhost:8083/ws/dashboard/live";

// Connects once to Dashboard Service's STOMP endpoint and fans live-metrics,
// live-alerts, live-predictions, and live-forecasts out to whichever components
// subscribe via the callbacks below. One socket for the whole app, not one per widget.
export function useLiveFeed({ onMetric, onAlert, onPrediction, onForecast } = {}) {
  const [connected, setConnected] = useState(false);
  const callbacksRef = useRef({ onMetric, onAlert, onPrediction, onForecast });
  callbacksRef.current = { onMetric, onAlert, onPrediction, onForecast };

  useEffect(() => {
    const client = new Client({
      webSocketFactory: () => new SockJS(WS_URL),
      reconnectDelay: 4000,
      onConnect: () => {
        setConnected(true);
        client.subscribe("/topic/live-metrics", (msg) => {
          callbacksRef.current.onMetric?.(JSON.parse(msg.body));
        });
        client.subscribe("/topic/live-alerts", (msg) => {
          callbacksRef.current.onAlert?.(JSON.parse(msg.body));
        });
        client.subscribe("/topic/live-predictions", (msg) => {
          callbacksRef.current.onPrediction?.(JSON.parse(msg.body));
        });
        client.subscribe("/topic/live-forecasts", (msg) => {
          callbacksRef.current.onForecast?.(JSON.parse(msg.body));
          console.log(msg.body);
        });
      },
      onDisconnect: () => setConnected(false),
      onWebSocketClose: () => setConnected(false),
    });

    client.activate();
    return () => client.deactivate();
  }, []);

  return { connected };
}
