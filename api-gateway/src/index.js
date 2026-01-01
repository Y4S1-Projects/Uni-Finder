import express from "express";
import cors from "cors";
import morgan from "morgan";
import dotenv from "dotenv";
import { createProxyMiddleware } from "http-proxy-middleware";

dotenv.config();

const PORT = process.env.PORT || 8080;
const FRONTEND_ORIGIN = process.env.FRONTEND_ORIGIN || "http://localhost:3000";
const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:5000";
const RECOMMENDATION_SERVICE_URL =
  process.env.RECOMMENDATION_SERVICE_URL || "http://localhost:5003";
const DEGREE_SERVICE_URL =
  process.env.DEGREE_SERVICE_URL || "http://localhost:5001";
const CAREER_SERVICE_URL =
  process.env.CAREER_SERVICE_URL || "http://localhost:5004";
const BUDGET_SERVICE_URL =
  process.env.BUDGET_SERVICE_URL || "http://localhost:5002";

const app = express();
app.use(express.json());
app.use(morgan("dev"));
app.use(cors({ origin: [FRONTEND_ORIGIN], credentials: true }));

const logProxyError = (label) => (err, req, res) => {
  console.error(`[Gateway:${label}]`, err.message, { url: req.originalUrl });
  if (!res.headersSent) {
    res.status(502).json({ message: "Upstream service unavailable" });
  }
};

app.get("/health", (req, res) => {
  res.json({
    status: "ok",
    gateway: "unifinder",
    upstreams: {
      backend: BACKEND_URL,
      recommendation: RECOMMENDATION_SERVICE_URL,
      budget: BUDGET_SERVICE_URL,
      degree: DEGREE_SERVICE_URL,
      career: CAREER_SERVICE_URL,
    },
  });
});

// Core backend (Express + Mongo)
app.use(
  createProxyMiddleware("/api", {
    target: BACKEND_URL,
    changeOrigin: true,
    proxyTimeout: 10_000,
    timeout: 10_000,
    pathRewrite: (path) => `/api${path}`,
    onError: logProxyError("backend"),
  })
);

// Travel/degree recommendation service (Flask)
app.use(
  createProxyMiddleware(["/recommend", "/best_recommendation"], {
    target: RECOMMENDATION_SERVICE_URL,
    changeOrigin: true,
    proxyTimeout: 20_000,
    timeout: 20_000,
    onError: logProxyError("recommendation"),
  })
);

// Degree recommendation (FastAPI) - exposed under /degree/*
app.use(
  createProxyMiddleware("/degree", {
    target: DEGREE_SERVICE_URL,
    changeOrigin: true,
    proxyTimeout: 20_000,
    timeout: 20_000,
    pathRewrite: { "^/degree": "" },
    onError: logProxyError("degree"),
  })
);

// Budget optimizer (Flask ML service)
app.use(
  createProxyMiddleware("/budget-service", {
    target: BUDGET_SERVICE_URL,
    changeOrigin: true,
    proxyTimeout: 20_000,
    timeout: 20_000,
    pathRewrite: { "^/budget-service": "" },
    onError: logProxyError("budget"),
  })
);

// Career service (FastAPI) - exposed under /career/*
app.use(
  createProxyMiddleware("/career", {
    target: CAREER_SERVICE_URL,
    changeOrigin: true,
    proxyTimeout: 20_000,
    timeout: 20_000,
    pathRewrite: { "^/career": "" },
    onError: logProxyError("career"),
  })
);

app.use((req, res) => {
  res.status(404).json({ message: "Route not found on API gateway" });
});

app.listen(PORT, () => {
  console.log(`API Gateway listening on http://localhost:${PORT}`);
  console.log(`→ Backend: ${BACKEND_URL}`);
  console.log(`→ Recommendation service: ${RECOMMENDATION_SERVICE_URL}`);
  console.log(`→ Degree service: ${DEGREE_SERVICE_URL}`);
  console.log(`→ Budget service: ${BUDGET_SERVICE_URL}`);
});
