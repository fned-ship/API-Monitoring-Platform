import { useCallback, useEffect, useMemo, useState } from "react";
import Header from "./components/Header";
import RiskPulse from "./components/RiskPulse";
import MetricStats from "./components/MetricStats";
import LatencyChart from "./components/LatencyChart";
import ForecastCards from "./components/ForecastCards";
import SignalFeed from "./components/SignalFeed";
import Toaster from "./components/Toaster";
import { api } from "./api/client";
import { useLiveFeed } from "./hooks/useLiveFeed";
import { useInterval } from "./hooks/useInterval";
import { useToasts } from "./hooks/useToasts";

const MAX_CHART_POINTS = 40;
const MAX_FEED_ITEMS = 40;
const POLL_INTERVAL_MS = 20000;

export default function App() {
  const [services, setServices] = useState([]);
  const [selectedService, setSelectedService] = useState("");
  const [latencyPoints, setLatencyPoints] = useState([]);
  const [forecastsByMetric, setForecastsByMetric] = useState({});
  const [currentRisk, setCurrentRisk] = useState({ riskScore: null, modelVersion: null });
  const [feedItems, setFeedItems] = useState([]);
  const [stats, setStats] = useState({ requestCount: null, avgLatencyMs: null, errorRatio: null });

  const { toasts, push: pushToast, dismiss: dismissToast } = useToasts();

  // --- bootstrap: known services ---
  useEffect(() => {
    api
      .listServices()
      .then((names) => {
        setServices(names);
        if (names.length > 0) setSelectedService((prev) => prev || names[0]);
      })
      .catch(() => {
        // Fallback: dashboard/services endpoint may not exist yet on an older backend —
        // the console still works once a service starts appearing via the live feed.
      });
  }, []);

  // useEffect(() => {
  //   console.log(latencyPoints)
  // }, [latencyPoints]);

  const addFeedItem = useCallback((item) => {
    setFeedItems((prev) => [item, ...prev].slice(0, MAX_FEED_ITEMS));
  }, []);

  // --- bootstrap + periodic sync for the selected service ---
  const loadServiceSnapshot = useCallback(async (serviceName) => {
  if (!serviceName) return;

  try {
    const metrics = await api.serviceMetrics(serviceName);
    const ascending = [...metrics].reverse().slice(-MAX_CHART_POINTS);

    // Merge new snapshot metrics with any active forecast points already in state
    setLatencyPoints((prevPoints) => {
      const existingForecasts = prevPoints.filter((p) => p.forecast !== null);

      const newActuals = ascending.map((m) => {
        const matchingForecast = prevPoints.find((p) => p.time === m.timestamp);
        return {
          time: m.timestamp,
          actual: m.responseTimeMs,
          forecast: matchingForecast ? matchingForecast.forecast : null,
        };
      });

      const combined = [...newActuals];

      for (const fPoint of existingForecasts) {
        if (!combined.some((p) => p.time === fPoint.time)) {
          combined.push(fPoint);
        }
      }

      combined.sort((a, b) => new Date(a.time) - new Date(b.time));
      return combined.slice(-MAX_CHART_POINTS - 5);
    });

    if (ascending.length > 0) {
      const avg = ascending.reduce((sum, m) => sum + (m.responseTimeMs || 0), 0) / ascending.length;
      const errors = ascending.filter((m) => m.statusCode >= 500).length;
      setStats({
        requestCount: ascending.length,
        avgLatencyMs: avg,
        errorRatio: errors / ascending.length,
      });
    }
  } catch {
    // service may not have any persisted metrics yet
  }

  try {
    const predictions = await api.recentPredictions();
    const forThisService = predictions.find((p) => p.serviceName === serviceName);
    if (forThisService) {
      setCurrentRisk({ riskScore: forThisService.riskScore, modelVersion: forThisService.modelVersion });
    }
  } catch {
    // ignore — prediction track may not have a promoted model yet
  }

  try {
    const alerts = await api.openAlerts();
    alerts
      .filter((a) => a.serviceName === serviceName)
      .forEach((a) =>
        addFeedItem({
          id: `alert-${a.id}`,
          kind: "alert",
          serviceName: a.serviceName,
          severity: a.severity,
          timestamp: a.triggeredAt,
          message: a.message,
          detail: a.alertType,
        })
      );
  } catch {
    // ignore
  }
}, [addFeedItem]);

  useEffect(() => {
    if (selectedService) loadServiceSnapshot(selectedService);
  }, [selectedService, loadServiceSnapshot]);

  useInterval(() => {
    if (selectedService) loadServiceSnapshot(selectedService);
  }, POLL_INTERVAL_MS);

  // --- live WebSocket feed ---
  const { connected } = useLiveFeed({
    onMetric: (event) => {
      if (event.serviceName !== selectedService) return;

      setLatencyPoints((prev) => {
        const points = [...prev];

        const index = points.findIndex(
          (p) => p.time === event.timestamp
        );

        if (index >= 0) {
          points[index] = {
            ...points[index],
            actual: event.responseTimeMs,
          };
        } else {
          points.push({
            time: event.timestamp,
            actual: event.responseTimeMs,
            forecast: null,
          });
        }

        points.sort((a, b) => new Date(a.time) - new Date(b.time));

        return points.slice(-MAX_CHART_POINTS - 5);
      });
    },

    onAlert: (event) => {
      addFeedItem({
        id: `alert-live-${event.alertId}`,
        kind: "alert",
        serviceName: event.serviceName,
        severity: event.severity,
        timestamp: event.triggeredAt,
        message: event.message,
        detail: event.alertType,
      });
      if (event.serviceName === selectedService || !selectedService) {
        pushToast({
          kind: "alert",
          serviceName: event.serviceName,
          severity: event.severity,
          message: event.message,
        });
      }
    },

    onPrediction: (event) => {
      addFeedItem({
        id: `pred-${event.predictionId}`,
        kind: "prediction",
        serviceName: event.serviceName,
        severity: event.severity,
        timestamp: event.generatedAt,
        message: `Risk ${Math.round(event.riskScore * 100)} — ${event.predictionType}`,
        detail: (event.contributingFeatures || []).join(", "),
      });
      if (event.serviceName === selectedService) {
        setCurrentRisk({ riskScore: event.riskScore, modelVersion: event.modelVersion });
      }
      if ((event.severity === "HIGH" || event.severity === "CRITICAL") && event.serviceName === selectedService) {
        pushToast({
          kind: "prediction",
          serviceName: event.serviceName,
          severity: event.severity,
          message: `Elevated risk detected (${Math.round(event.riskScore * 100)}) — ${event.predictionType}`,
        });
      }
    },

    onForecast: (event) => {
      console.log(event);
      if (event.serviceName !== selectedService) return;

      setForecastsByMetric((prev) => ({
        ...prev,
        [event.targetMetric]: event,
      }));

      if (event.targetMetric !== "avg_response_time_ms") return;

      // const targetTime = new Date(
      //   new Date(event.windowTimestamp).getTime() +
      //     event.horizonSeconds * 1000
      // ).toISOString();

      const baseTime =
        event.windowTimestamp &&
        event.windowTimestamp !== "1970-01-01T00:00:00Z"
          ? new Date(event.windowTimestamp)
          : new Date(event.generatedAt);

      const targetTime = new Date(
        baseTime.getTime() + event.horizonSeconds * 1000
      ).toISOString();




      setLatencyPoints((prevPoints) => {
        const points = [...prevPoints];

        const existingIndex = points.findIndex(
          (p) => p.time === targetTime
        );

        if (existingIndex >= 0) {
          // Existing point (actual or previous forecast)
          points[existingIndex] = {
            ...points[existingIndex],
            forecast: event.predictedValue,
          };
        } else {
          // Future forecast point
          points.push({
            time: targetTime,
            actual: null,
            forecast: event.predictedValue,
          });
        }

        points.sort((a, b) => new Date(a.time) - new Date(b.time));

        return points.slice(-MAX_CHART_POINTS - 5);
      });
    },
  });

  const chartData = useMemo(() => latencyPoints, [latencyPoints]);

  return (
    <div className="flex h-screen flex-col">
      <Header
        services={services}
        selectedService={selectedService}
        onSelectService={setSelectedService}
        connected={connected}
      />

      <main className="grid flex-1 grid-cols-12 gap-5 overflow-hidden p-6">
        <section className="col-span-8 flex flex-col gap-5 overflow-y-auto pr-1">
          <MetricStats {...stats} />
          <LatencyChart data={chartData} />
          <div>
            <h3 className="mb-3 text-[11px] tracking-[0.15em] text-ink-faint uppercase">
              Forecasts — next 5 minutes
            </h3>
            <ForecastCards forecasts={forecastsByMetric} />
          </div>
        </section>

        <aside className="col-span-4 flex flex-col gap-5 overflow-hidden">
          <div className="rounded-lg border border-panel-line bg-panel">
            <RiskPulse
              riskScore={currentRisk.riskScore ?? 0}
              modelVersion={currentRisk.modelVersion}
              hasModel={currentRisk.riskScore !== null}
            />
          </div>
          <div className="min-h-0 flex-1">
            <SignalFeed items={feedItems} />
          </div>
        </aside>
      </main>

      <Toaster toasts={toasts} onDismiss={dismissToast} />
    </div>
  );
}

