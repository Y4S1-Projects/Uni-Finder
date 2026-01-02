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

const TARGET_BACKEND = BACKEND_URL || "http://localhost:5000";
const TARGET_RECO = RECOMMENDATION_SERVICE_URL || "http://localhost:5003";
const TARGET_DEGREE = DEGREE_SERVICE_URL || "http://localhost:5001";
const TARGET_BUDGET = BUDGET_SERVICE_URL || "http://localhost:5002";
const TARGET_CAREER = CAREER_SERVICE_URL || "http://localhost:5004";

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
      backend: TARGET_BACKEND,
      recommendation: TARGET_RECO,
      budget: TARGET_BUDGET,
      degree: TARGET_DEGREE,
      career: TARGET_CAREER,
    },
  });
});

// Core backend (Express + Mongo)
const backendProxy = createProxyMiddleware({
	target: TARGET_BACKEND,
	changeOrigin: true,
	proxyTimeout: 10_000,
	timeout: 10_000,
	onError: logProxyError("backend"),
});
app.use("/api", backendProxy);

// Place recommendation service (Flask)
const recommendationProxy = createProxyMiddleware({
	target: TARGET_RECO,
	changeOrigin: true,
	proxyTimeout: 20_000,
	timeout: 20_000,
	onError: logProxyError("recommendation"),
});
app.use(["/recommend", "/best_recommendation"], recommendationProxy);

// Degree recommendation (FastAPI) - exposed under /degree/*
const degreeProxy = createProxyMiddleware({
	target: TARGET_DEGREE,
	changeOrigin: true,
	proxyTimeout: 20_000,
	timeout: 20_000,
	pathRewrite: { "^/degree": "" },
	onError: logProxyError("degree"),
});
app.use("/degree", degreeProxy);

// Budget optimizer (Flask ML service)
const budgetProxy = createProxyMiddleware({
	target: TARGET_BUDGET,
	changeOrigin: true,
	proxyTimeout: 20_000,
	timeout: 20_000,
	pathRewrite: { "^/budget-service": "" },
	onError: logProxyError("budget"),
});
app.use("/budget-service", budgetProxy);

// Career service (new proxy)
const careerProxy = createProxyMiddleware({
  target: TARGET_CAREER,
  changeOrigin: true,
  proxyTimeout: 20_000,
  timeout: 20_000,
  pathRewrite: { "^/career": "" },
  onProxyReq(proxyReq, req, res) {
    if (req.body) {
      const bodyData = JSON.stringify(req.body);
      proxyReq.setHeader("Content-Type", "application/json");
      proxyReq.setHeader("Content-Length", Buffer.byteLength(bodyData));
      proxyReq.write(bodyData);
    }
  },
  onError: logProxyError("career"),
});

app.use("/career", careerProxy);

app.use((req, res) => {
  res.status(404).json({ message: "Route not found on API gateway" });
});

app.listen(PORT, () => {
  console.log(`API Gateway listening on http://localhost:${PORT}`);
  console.log(`→ Backend: ${BACKEND_URL}`);
  console.log(`→ Recommendation service: ${RECOMMENDATION_SERVICE_URL}`);
  console.log(`→ Degree service: ${DEGREE_SERVICE_URL}`);
  console.log(`→ Budget service: ${BUDGET_SERVICE_URL}`);
  console.log(`→ Career service: ${CAREER_SERVICE_URL}`);
});
