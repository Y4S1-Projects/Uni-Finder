# Degree Recommendation Service (FastAPI)

## Ports (local dev)

- Service: `http://127.0.0.1:5001`
- API Gateway: `http://localhost:8080`
- Frontend must call the gateway only.

## Run (Windows)

Simplest (recommended):

- `python main.py`

Alternative (Python runner):

- `python run.py`

Alternative (batch script):

- Run `run_dev.bat`

Or run uvicorn explicitly on port 5001:

- `python -m uvicorn main:app --reload --host 127.0.0.1 --port 5001`

## API via Gateway

Call through the gateway (do not call `:5001` from the browser):

- `POST http://localhost:8080/degree/recommend`

Health checks:

- `GET http://127.0.0.1:5001/health`
- `GET http://localhost:8080/health`
