// All REST calls go through the API Gateway (port 8080), which already routes
// /dashboard/** -> Dashboard Service and /alerts/** -> Alert Service (Phase 1 Step 8).
// This keeps the frontend pointed at one origin instead of hardcoding every service's port.
const GATEWAY_URL = import.meta.env.VITE_GATEWAY_URL || "http://localhost:8080";

async function getJson(path) {
  const res = await fetch(`${GATEWAY_URL}${path}`);
  if (!res.ok) {
    throw new Error(`Request failed: ${path} (${res.status})`);
  }
  return res.json();
}

export const api = {
  // --- known services (new endpoint, see backend addition in the guide) ---
  listServices: () => getJson(`/dashboard/services`),

  // --- overview + per-service metrics (existing Dashboard Service endpoints) ---
  overview: () => getJson(`/dashboard/overview`),
  serviceMetrics: (serviceName) =>
    getJson(`/dashboard/services/${encodeURIComponent(serviceName)}`),

  // --- alerts (existing Alert Service endpoints, via gateway) ---
  openAlerts: () => getJson(`/alerts?status=OPEN`),

  // --- AI predictions (existing Dashboard Service endpoints, Phase 2b) ---
  recentPredictions: () => getJson(`/dashboard/predictions`),
  atRiskPredictions: () => getJson(`/dashboard/predictions/at-risk`),

  // --- AI forecasts (existing Dashboard Service endpoints, Phase 2c) ---
  forecasts: (serviceName, metric) =>
    getJson(
      `/dashboard/forecasts?serviceName=${encodeURIComponent(serviceName)}&metric=${encodeURIComponent(metric)}`
    ),
  trendingForecasts: () => getJson(`/dashboard/forecasts/trending`),
};
