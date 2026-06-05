const express = require("express");
const client = require("prom-client");

const app = express();
const port = process.env.PORT || 3000;
const serviceName = process.env.SERVICE_NAME || "cloudmaven-backend";

client.collectDefaultMetrics({
  labels: { service: serviceName }
});

const requestCounter = new client.Counter({
  name: "cloudmaven_api_requests_total",
  help: "Total API requests",
  labelNames: ["method", "route", "status_code"]
});

const latencyHistogram = new client.Histogram({
  name: "cloudmaven_api_request_duration_seconds",
  help: "API request latency in seconds",
  labelNames: ["method", "route", "status_code"],
  buckets: [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5]
});

function log(level, message, fields = {}) {
  console.log(JSON.stringify({
    timestamp: new Date().toISOString(),
    level,
    service: serviceName,
    message,
    ...fields
  }));
}

app.use(express.json());

app.use((req, res, next) => {
  const start = process.hrtime.bigint();
  res.on("finish", () => {
    const durationSeconds = Number(process.hrtime.bigint() - start) / 1e9;
    const route = req.route?.path || req.path;
    requestCounter.inc({ method: req.method, route, status_code: res.statusCode });
    latencyHistogram.observe({ method: req.method, route, status_code: res.statusCode }, durationSeconds);
    log(res.statusCode >= 500 ? "error" : "info", "request completed", {
      method: req.method,
      path: req.path,
      route,
      status_code: res.statusCode,
      duration_ms: Math.round(durationSeconds * 1000)
    });
  });
  next();
});

app.get("/health", (_req, res) => {
  res.json({ status: "ok", service: serviceName });
});

app.get("/api", (_req, res) => {
  res.json({
    message: "Hello from CloudMaven backend",
    service: serviceName,
    time: new Date().toISOString()
  });
});

app.get("/api/error", (_req, res) => {
  log("error", "simulated error endpoint called", { endpoint: "/api/error" });
  res.status(500).json({ error: "simulated error" });
});

app.get("/metrics", async (_req, res) => {
  res.set("Content-Type", client.register.contentType);
  res.end(await client.register.metrics());
});

app.listen(port, () => {
  log("info", "backend started", { port });
});

