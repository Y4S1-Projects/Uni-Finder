---
title: Uni-Finder Backend Monolith
emoji: "🎓"
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
short_description: Multi-service backend for Uni-Finder (Node + FastAPI + Flask) behind Nginx.
---

# Uni-Finder Backend Monolith

This Hugging Face Space runs the Uni-Finder backend stack as a single Docker app.

## Exposed routes

- `/api` -> Node backend
- `/degree` -> Degree recommendation service
- `/budget` -> Budget optimizer service
- `/career` -> Career guidance service
- `/scholarship` -> Scholarship/loan matcher service

## Health checks

- `/health`
- `/degree/health`
- `/budget/health`
- `/career/health`
- `/scholarship/health`
