const express = require("express");

const app = express();
const port = process.env.PORT || 8080;
const apiUrl = process.env.API_URL || "http://cloudmaven-backend:3000";

app.get("/health", (_req, res) => {
  res.json({ status: "ok", service: "cloudmaven-frontend" });
});

app.get("/", (_req, res) => {
  res.type("html").send(`<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CloudMaven DevOps Assessment</title>
  <style>
    body { margin: 0; font-family: Arial, sans-serif; background: #f7f9fb; color: #17202a; }
    main { max-width: 880px; margin: 64px auto; padding: 32px; background: #fff; border: 1px solid #d8dee6; border-radius: 8px; }
    h1 { margin-top: 0; font-size: 34px; }
    code { background: #eef2f6; padding: 2px 6px; border-radius: 4px; }
    button { border: 0; background: #1769aa; color: #fff; padding: 10px 14px; border-radius: 6px; cursor: pointer; }
    pre { white-space: pre-wrap; background: #101820; color: #d7f7d7; padding: 16px; border-radius: 6px; min-height: 72px; }
  </style>
</head>
<body>
  <main>
    <h1>CloudMaven DevOps Assessment</h1>
    <p>Two-tier Node.js app running on Kubernetes. Backend target: <code>${apiUrl}</code></p>
    <button id="call-api">Call Backend API</button>
    <pre id="result">Waiting for request...</pre>
  </main>
  <script>
    document.getElementById("call-api").addEventListener("click", async () => {
      const result = document.getElementById("result");
      result.textContent = "Calling backend...";
      try {
        const response = await fetch("/api");
        result.textContent = JSON.stringify(await response.json(), null, 2);
      } catch (error) {
        result.textContent = error.message;
      }
    });
  </script>
</body>
</html>`);
});

app.get("/api", async (_req, res) => {
  const response = await fetch(`${apiUrl}/api`);
  res.status(response.status).json(await response.json());
});

app.listen(port, () => {
  console.log(JSON.stringify({
    timestamp: new Date().toISOString(),
    level: "info",
    service: "cloudmaven-frontend",
    message: "frontend started",
    port,
    api_url: apiUrl
  }));
});

