@echo off
setlocal
REM Run the Degree Recommendation Service on the standardized port (5001).
REM This avoids uvicorn's default port 8000.

set PORT=5001
python -m uvicorn main:app --reload --host 127.0.0.1 --port %PORT%
