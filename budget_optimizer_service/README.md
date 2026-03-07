# Budget Optimizer Service

Standalone Python microservice for the **UniFinder LK** AI-Powered Student Budget Optimizer.
No database connectivity — pure Flask REST API backed by ML models and CSV data.

---

## Folder Structure

```
budget_optimizer_service/
├── app.py                        ← Flask API entry point (port 5002)
├── budget_calculator.py          ← Food & transport cost calculator
├── ml_budget_predictor.py        ← ML budget prediction + optimal strategy
├── model_performance_dashboard.py← Model accuracy/performance metrics
├── requirements.txt              ← Python dependencies
├── .env                          ← API keys (OPENAI_API_KEY)
├── .env.example                  ← .env template
│
├── data/                         ← CSV datasets + trained ML model files
│   ├── food_prices.csv
│   ├── Vegetables_fruit_prices.csv
│   ├── srilanka_transport_costs.csv
│   ├── room_annex_rentals.csv
│   ├── academic_calendar.csv
│   ├── interestRates.csv
│   ├── Student Budget Survey.csv
│   ├── budget_optimizer_gbr_model_final_optimized.pkl   ← GBR optimizer model
│   ├── risk_classifier_model_final.pkl                  ← Risk classifier
│   └── feature_preprocessor_final.pkl                  ← Feature scaler
│
├── templates/                    ← HTML templates for web view
│   ├── budget_optimizer.html
│   └── best_recommendation.html
│
└── notebooks/
    └── Student_Budget_ML_Training_ADVANCED.ipynb        ← Model training
```

---

## Quick Start

```bash
# 1. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set OpenAI API key (for AI Enhanced Strategy feature)
cp .env.example .env
# Edit .env and add:  OPENAI_API_KEY=sk-...

# 4. Run the service
python3 app.py
# Server: http://127.0.0.1:5002
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | `/health` | Health check |
| POST | `/api/budget/calculate-food` | Auto-calculate food budget |
| POST | `/api/budget/calculate-transport` | Auto-calculate transport budget |
| POST | `/api/budget/complete-analysis` | Full ML budget analysis |
| POST | `/api/budget/gemini-strategy` | AI step-by-step strategy (OpenAI) |
| GET  | `/api/data/districts` | List of Sri Lanka districts |
| GET  | `/api/data/universities` | List of universities |
| GET  | `/api/data/food-prices?district=Colombo` | Food prices by district |
| GET  | `/api/data/transport-costs?source=Colombo&destination=Kandy` | Route cost |
| GET  | `/api/data/rental-prices?district=Colombo` | Avg rent by district |
| GET  | `/api/model/performance` | ML model accuracy metrics |

---

## ML Models

| Model | File | Accuracy |
|-------|------|----------|
| GBR Budget Optimizer | `data/budget_optimizer_gbr_model_final_optimized.pkl` | 86.89% |
| Risk Classifier | `data/risk_classifier_model_final.pkl` | 82.5% |
| Feature Preprocessor | `data/feature_preprocessor_final.pkl` | — |

---

## No Database Required

This service is completely self-contained:
- No MongoDB, Node.js, or external DB connections
- All reference data is in `data/*.csv`
- All ML models are in `data/*.pkl`
- API keys only needed for the optional OpenAI AI strategy feature
