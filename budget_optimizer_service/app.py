#!/usr/bin/env python3
"""
Enhanced Budget Optimizer API - Complete Implementation
Integrates with actual CSV data and ML models
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv
import time
import hashlib
import json
from functools import lru_cache

# Load environment variables from .env file
load_dotenv()

# Try to import OpenAI (optional)
try:
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️  OpenAI not installed. Run: pip install openai")

# Import our custom modules
from budget_calculator import BudgetCalculator
from ml_budget_predictor import MLBudgetPredictor

app = Flask(__name__)


def _build_cors_origins():
    cors_env = os.getenv("CORS_ORIGINS", "").strip()
    if cors_env == "*":
        return "*"
    if cors_env:
        return [origin.strip() for origin in cors_env.split(",") if origin.strip()]
    return [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


cors_origins = _build_cors_origins()
if cors_origins == "*":
    CORS(app)
else:
    CORS(app, origins=cors_origins)

# ── Paths ──────────────────────────────────────────────────────────
DATA_DIR = "data"  # CSV data & trained model files live in data/

# Initialize components
calculator = BudgetCalculator(data_dir=DATA_DIR)
ml_predictor = MLBudgetPredictor(model_dir=DATA_DIR)

# AI API cache (simple in-memory cache with 1-hour TTL)
openai_cache = {}
CACHE_TTL_SECONDS = 3600  # 1 hour
PROMPT_VERSION = "v4-min-savings-buffer"  # bump this whenever the prompt changes

# Load OpenAI API key
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

print("🚀 Budget Optimizer API Starting...")
print("=" * 60)
print(f"🤖 AI Service: OpenAI (GPT-4o-mini)")
print(
    f"   Status: {'✅ Configured' if OPENAI_API_KEY and OPENAI_AVAILABLE else '❌ No API Key or Not Installed'}"
)
print("=" * 60)


# ═══════════════════════════════════════════════════════════════════
#  OPENAI API HELPERS WITH RETRY LOGIC & CACHING
# ═══════════════════════════════════════════════════════════════════


def create_cache_key(data):
    """Create a cache key from request data"""
    # Use income, expenses, risk level AND prompt version so prompt changes bust the cache
    financial = data.get("financial_summary", {})
    key_data = {
        "income": financial.get("monthly_income", 0),
        "expenses": financial.get("total_expenses", 0),
        "savings_rate": financial.get("savings_rate", 0),
        "risk": data.get("risk_assessment", {}).get("risk_level", ""),
        "prompt_version": PROMPT_VERSION,
    }
    key_string = json.dumps(key_data, sort_keys=True)
    return hashlib.md5(key_string.encode()).hexdigest()


def get_cached_openai_response(cache_key):
    """Get cached OpenAI response if valid"""
    if cache_key in openai_cache:
        cached_data, timestamp = openai_cache[cache_key]
        age = time.time() - timestamp
        if age < CACHE_TTL_SECONDS:
            print(f"✅ Using cached OpenAI response (age: {int(age)}s)")
            return cached_data
        else:
            print(f"⏰ Cache expired (age: {int(age)}s, TTL: {CACHE_TTL_SECONDS}s)")
            del openai_cache[cache_key]
    return None


def cache_openai_response(cache_key, response):
    """Cache an OpenAI response"""
    openai_cache[cache_key] = (response, time.time())
    print(f"💾 Cached OpenAI response")


def call_openai_with_retry(api_key, prompt, max_retries=2):
    """
    Call OpenAI API (GPT-4o-mini) with retry logic

    Args:
        api_key: OpenAI API key
        prompt: Text prompt for GPT
        max_retries: Maximum number of retry attempts

    Returns:
        tuple: (success: bool, response: str|dict, error_msg: str|None)
    """
    if not OPENAI_AVAILABLE:
        return False, None, "OpenAI library not installed. Run: pip install openai"

    for attempt in range(max_retries):
        try:
            print(f"📡 Calling OpenAI API (attempt {attempt + 1}/{max_retries})...")

            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Fast, affordable model
                messages=[
                    {
                        "role": "system",
                        "content": "You are a friendly, expert financial advisor for Sri Lankan university students.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=1024,
            )

            content = response.choices[0].message.content
            print(f"✅ OpenAI API success ({len(content)} chars)")
            return True, content, None

        except Exception as e:
            error_str = str(e)
            print(f"⚠️ OpenAI API error: {error_str[:200]}")

            # Rate limit - retry with backoff
            if "rate_limit" in error_str.lower() or "429" in error_str:
                if attempt < max_retries - 1:
                    wait_time = (2**attempt) + (time.time() % 1)
                    print(f"⏳ Rate limit hit. Waiting {wait_time:.1f}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    return False, None, f"OpenAI rate limit exceeded: {error_str[:200]}"

            # Auth error - don't retry
            elif "auth" in error_str.lower() or "api_key" in error_str.lower():
                return False, None, f"OpenAI authentication failed: {error_str[:200]}"

            # Other errors - retry once
            elif attempt < max_retries - 1:
                wait_time = 2**attempt
                print(f"⏳ Retrying in {wait_time:.1f}s...")
                time.sleep(wait_time)
                continue
            else:
                return (
                    False,
                    None,
                    f"OpenAI error after {max_retries} attempts: {error_str[:200]}",
                )

    return False, None, "Max retries exceeded"


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify(
        {
            "status": "healthy",
            "message": "Budget Optimizer API is running",
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.route("/api/budget/calculate-food", methods=["POST"])
def calculate_food_budget():
    """
    Calculate food budget based on user preferences

    Request Body:
    {
        "food_type": "Home Cooked" | "Mixed" | "Food Delivery" | "Mostly Canteen/Restaurants" | "Full Meal Plan",
        "meals_per_day": "2 meals" | "3 meals" | "3 meals + snacks",
        "diet_type": "Vegetarian" | "Non-Vegetarian" | "Vegan",
        "cooking_frequency": "Every day" | "Most days" | "Sometimes" | "Rarely" | "Never",
        "district": "Colombo" | "Kandy" | ...,
        "grocery_items": {...},  // If Home Cooked
        "delivery_items": {...},  // If Food Delivery
        "cooking_percentage": 60  // If Mixed
    }
    """
    try:
        food_data = request.json

        # Calculate food budget
        result = calculator.calculate_food_budget(food_data)

        return jsonify({"success": True, "food_budget": result})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/budget/calculate-transport", methods=["POST"])
def calculate_transport_budget():
    """
    Calculate transport budget

    Request Body:
    {
        "distance_uni_accommodation": 5,
        "distance_home_uni": 80,
        "transport_method": "Bus" | "Train" | "Tuk-Tuk" | etc.,
        "days_per_week": "5 days",
        "home_visit_frequency": "Monthly" | "Weekly" | etc.,
        "transport_method_home": "Bus"
    }
    """
    try:
        transport_data = request.json

        # Calculate transport budget
        result = calculator.calculate_transport_budget(transport_data)

        return jsonify({"success": True, "transport_budget": result})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/budget/predict", methods=["POST"])
def predict_budget():
    """
    AI-powered budget prediction using ML models

    Request Body:
    {
        "monthly_income": 30000,
        "year_of_study": "Second Year",
        "field_of_study": "Engineering",
        "district": "Colombo",
        "accommodation_type": "Rented Room",
        "rent": 10000,
        "food_budget": 12000,
        "transport_budget": 5000,
        "university": "SLIIT",
        ...
    }
    """
    try:
        student_data = request.json

        # Get ML prediction
        prediction = ml_predictor.predict_budget(student_data)

        # Get risk assessment
        risk_assessment = ml_predictor.predict_risk(student_data)

        return jsonify(
            {
                "success": True,
                "prediction": prediction,
                "risk_assessment": risk_assessment,
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/budget/complete-analysis", methods=["POST"])
def complete_budget_analysis():
    """
    Complete budget analysis with all calculations

    This is the MAIN endpoint that combines everything:
    1. Food budget calculation
    2. Transport budget calculation
    3. ML prediction
    4. Risk assessment
    5. Personalized recommendations
    """
    try:
        data = request.json

        print(f"📊 Processing complete budget analysis for student...")

        # Step 1: Calculate Food Budget
        food_data = {
            "food_type": data.get("food_type", "Mixed"),
            "meals_per_day": data.get("meals_per_day", "3 meals"),
            "diet_type": data.get("diet_type", "Vegetarian"),
            "cooking_frequency": data.get("cooking_frequency", "Most days"),
            "district": data.get("district", "Colombo"),
            "grocery_items": data.get("grocery_items", {}),
            "delivery_items": data.get("delivery_items", {}),
            "cooking_percentage": data.get("cooking_percentage", 60),
            "monthly_income": data.get("monthly_income", 25000),
        }

        food_budget = calculator.calculate_food_budget(food_data)
        print(f"✅ Food Budget: LKR {food_budget['monthly_total']}")

        # Step 2: Calculate Transport Budget
        transport_data = {
            "distance_uni_accommodation": data.get("distance_uni_accommodation", 5),
            "distance_home_uni": data.get("distance_home_uni", 50),
            "transport_method": data.get("transport_method", "Bus"),
            "days_per_week": data.get("days_per_week", "5 days"),
            "home_visit_frequency": data.get("home_visit_frequency", "Monthly"),
            # Home route — accept both field names
            "transport_method_home_accommodation": data.get(
                "transport_method_home_accommodation",
                data.get("transport_method_home", "Bus"),
            ),
            "transport_method_home": data.get("transport_method_home", "Bus"),
            # Work commute (new fields)
            "has_work_commute": data.get("has_work_commute", False),
            "distance_work": data.get("distance_work", 10),
            "work_transport_method": data.get("work_transport_method", "Bus"),
            "work_days_per_week": data.get("work_days_per_week", "5 days"),
        }

        transport_budget = calculator.calculate_transport_budget(transport_data)
        print(f"✅ Transport Budget: LKR {transport_budget['monthly_total']}")

        # Step 3: Prepare student data for ML prediction
        # ── Include 'money from home' as additional income source ──
        base_income = data.get("monthly_income", 25000)
        home_money = data.get("home_money", 0)  # NEW: money sent from family
        monthly_income_total = base_income + home_money  # effective total income

        student_data = {
            "monthly_income": monthly_income_total,
            "year_of_study": data.get("year_of_study", "Second Year"),
            "field_of_study": data.get("field_of_study", "IT"),
            "district": data.get("district", "Colombo"),
            "accommodation_type": data.get("accommodation_type", "Rented Room"),
            "rent": data.get("rent", 8000),
            "food_budget": food_budget["monthly_total"],
            "transport_budget": transport_budget["monthly_total"],
            "transport_method": data.get("transport_method", "Bus"),
            "food_type": data.get("food_type", "Mixed"),
            "university": data.get("university", "SLIIT"),
            "meals_per_day": data.get("meals_per_day", "3 meals"),
            "home_visit_frequency": data.get("home_visit_frequency", "Monthly"),
            "cooking_percentage": data.get("cooking_percentage", 60),
            "diet_type": data.get("diet_type", "Vegetarian"),
            "distance_uni_accommodation": data.get("distance_uni_accommodation", 5),
        }

        # Step 4: Get ML predictions and risk assessment
        complete_analysis = ml_predictor.generate_complete_analysis(student_data)
        print(f"✅ ML Analysis Complete")

        # Step 5: Calculate total expenses
        rent = data.get("rent", 8000)
        internet = data.get("internet", 1500)
        study_materials = data.get("study_materials", 2000)
        entertainment = data.get("entertainment", 2000)
        utilities = data.get("utilities", 1000)
        healthcare = data.get("healthcare", 1000)
        other = data.get("other", 500)

        calculated_total_expenses = (
            rent
            + food_budget["monthly_total"]
            + transport_budget["monthly_total"]
            + internet
            + study_materials
            + entertainment
            + utilities
            + healthcare
            + other
        )

        monthly_income = monthly_income_total  # use the combined income
        calculated_savings = monthly_income - calculated_total_expenses
        savings_rate = (
            (calculated_savings / monthly_income * 100) if monthly_income > 0 else 0
        )

        # Step 5.5: Generate Optimal Budget Strategy (NEW FEATURE!)
        current_expense_breakdown = {
            "rent": rent,
            "food": food_budget["monthly_total"],
            "transport": transport_budget["monthly_total"],
            "internet": internet,
            "study_materials": study_materials,
            "entertainment": entertainment,
            "utilities": utilities,
            "healthcare": healthcare,
            "other": other,
            "total_expenses": calculated_total_expenses,
        }

        optimal_strategy = ml_predictor.generate_optimal_budget_strategy(
            student_data, current_expense_breakdown
        )
        print(
            f"✅ Optimal Strategy Generated - Potential Savings: LKR {optimal_strategy['maximum_savings_potential']}"
        )

        # Step 6: Build comprehensive response
        response = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            # Calculated budgets
            "calculated_budgets": {"food": food_budget, "transport": transport_budget},
            # Expense breakdown
            "expense_breakdown": {
                "rent": rent,
                "food": round(food_budget["monthly_total"], 2),
                "transport": round(transport_budget["monthly_total"], 2),
                "internet": internet,
                "study_materials": study_materials,
                "entertainment": entertainment,
                "utilities": utilities,
                "healthcare": healthcare,
                "other": other,
                "total_expenses": round(calculated_total_expenses, 2),
            },
            # Financial summary
            "financial_summary": {
                "monthly_income": monthly_income,
                "base_income": base_income,
                "home_money": home_money,
                "total_expenses": round(calculated_total_expenses, 2),
                "monthly_savings": round(calculated_savings, 2),
                "savings_rate": round(savings_rate, 1),
            },
            # ML predictions
            "ml_prediction": complete_analysis.get("budget_prediction"),
            "risk_assessment": complete_analysis.get("risk_assessment"),
            # Overall recommendation
            "recommendation": complete_analysis.get("recommendation"),
            "optimization_status": complete_analysis["financial_summary"].get(
                "optimization_status"
            ),
            # 🆕 NEW: Optimal Budget Strategy
            "optimal_strategy": optimal_strategy,
        }

        print(f"✅ Complete analysis returned successfully")
        print(
            f"   Income: LKR {monthly_income} | Expenses: LKR {round(calculated_total_expenses, 2)} | Savings: LKR {round(calculated_savings, 2)}"
        )

        return jsonify(response)

    except Exception as e:
        print(f"❌ Error in complete analysis: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/data/districts", methods=["GET"])
def get_districts():
    """Get list of all districts"""
    districts = [
        "Colombo",
        "Gampaha",
        "Kalutara",
        "Kandy",
        "Matale",
        "Nuwara Eliya",
        "Galle",
        "Matara",
        "Hambantota",
        "Jaffna",
        "Kilinochchi",
        "Mannar",
        "Vavuniya",
        "Mullaitivu",
        "Batticaloa",
        "Ampara",
        "Trincomalee",
        "Kurunegala",
        "Puttalam",
        "Anuradhapura",
        "Polonnaruwa",
        "Badulla",
        "Monaragala",
        "Ratnapura",
        "Kegalle",
    ]
    return jsonify({"districts": districts})


@app.route("/api/data/universities", methods=["GET"])
def get_universities():
    """Get list of universities"""
    universities = [
        "University of Colombo",
        "University of Peradeniya",
        "University of Kelaniya",
        "University of Moratuwa",
        "University of Ruhuna",
        "University of Jaffna",
        "SLIIT",
        "NSBM Green University",
        "IIT Campus",
        "Informatics Institute",
        "Other",
    ]
    return jsonify({"universities": universities})


@app.route("/api/data/food-prices", methods=["GET"])
def get_food_prices():
    """Get food prices by district"""
    try:
        district = request.args.get("district", "Colombo")

        # Load food prices
        food_prices_path = os.path.join(DATA_DIR, "food_prices.csv")
        if os.path.exists(food_prices_path):
            df = pd.read_csv(food_prices_path)
            district_prices = df[df["District"] == district]

            if not district_prices.empty:
                prices = district_prices[["Item_Name", "Price (LKR)"]].to_dict(
                    "records"
                )
                return jsonify(
                    {"success": True, "district": district, "prices": prices}
                )

        return jsonify({"success": False, "error": "Food prices not found"}), 404

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/data/transport-costs", methods=["GET"])
def get_transport_costs():
    """Get transport costs between districts"""
    try:
        source = request.args.get("source", "Colombo")
        destination = request.args.get("destination", "Kandy")

        # Load transport costs
        transport_path = os.path.join(DATA_DIR, "srilanka_transport_costs.csv")
        if os.path.exists(transport_path):
            df = pd.read_csv(transport_path)
            route = df[
                (df["Source_District"] == source)
                & (df["Destination_District"] == destination)
            ]

            if not route.empty:
                result = route.iloc[0].to_dict()
                return jsonify({"success": True, "route": result})

        return jsonify({"success": False, "error": "Route not found"}), 404

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/data/rental-prices", methods=["GET"])
def get_rental_prices():
    """Get average rental prices by district"""
    try:
        district = request.args.get("district", "Colombo")

        # Load rental data
        rental_path = os.path.join(DATA_DIR, "room_annex_rentals.csv")
        if os.path.exists(rental_path):
            df = pd.read_csv(rental_path)

            # Filter by district (case-insensitive partial match)
            district_rentals = df[
                df["District"].str.contains(district, case=False, na=False)
            ]

            if not district_rentals.empty:
                avg_price = district_rentals["Cleaned_Price"].mean()
                min_price = district_rentals["Cleaned_Price"].min()
                max_price = district_rentals["Cleaned_Price"].max()

                return jsonify(
                    {
                        "success": True,
                        "district": district,
                        "average_rent": round(avg_price, 2),
                        "min_rent": round(min_price, 2),
                        "max_rent": round(max_price, 2),
                        "sample_count": len(district_rentals),
                    }
                )

        return (
            jsonify(
                {
                    "success": False,
                    "error": "Rental data not found",
                    "suggestion": "Using default estimates",
                }
            ),
            404,
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/model/performance", methods=["GET"])
def get_model_performance():
    """Get ML model performance metrics"""
    try:
        performance = {
            "status": "ready",
            "models_loaded": {
                "gbr_optimizer": ml_predictor.gbr_model is not None,
                "risk_classifier": ml_predictor.risk_classifier is not None,
                "feature_preprocessor": ml_predictor.feature_preprocessor is not None,
            },
            "accuracy_metrics": {
                "expense_prediction": {
                    "accuracy": 86.89,
                    "model_type": "Gradient Boosting Regressor",
                },
                "risk_classification": {
                    "accuracy": 82.5,
                    "model_type": "Logistic Regression",
                },
            },
            "data_sources": {
                "training_samples": 1020,
                "food_price_items": 402,
                "transport_routes": 100,
                "rental_listings": 669,
            },
        }

        return jsonify(performance)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/budget/gemini-strategy", methods=["POST"])
def get_ai_strategy():
    """
    Call OpenAI API to generate enhanced, personalized budget strategy.
    Uses GPT-4o-mini model for fast, accurate financial advice.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Check if OpenAI is configured
        if not OPENAI_API_KEY or not OPENAI_AVAILABLE:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "OpenAI not configured",
                        "setup_guide": "Add OPENAI_API_KEY to backend/.env file (https://platform.openai.com/api-keys)",
                    }
                ),
                503,
            )

        # Check cache first
        cache_key = create_cache_key(data)
        cached_response = get_cached_openai_response(cache_key)
        if cached_response:
            return jsonify(
                {
                    "success": True,
                    "ai_strategy": cached_response,
                    "ai_provider": "OpenAI",
                    "cached": True,
                    "timestamp": datetime.now().isoformat(),
                }
            )

        # Extract data from request
        financial_summary = data.get("financial_summary", {})
        expense_breakdown = data.get("expense_breakdown", {})
        risk_assessment = data.get("risk_assessment", {})
        optimal_strategy = data.get("optimal_strategy", {})
        student_profile = data.get("student_profile", {})

        # ── Build a rich, structured prompt for AI ──────────────────
        income = financial_summary.get("monthly_income", 0)
        total_exp = financial_summary.get("total_expenses", 0)
        savings = financial_summary.get("monthly_savings", 0)
        savings_rate = financial_summary.get("savings_rate", 0)
        risk_level = risk_assessment.get("risk_level", "Unknown")
        risk_pct = risk_assessment.get("risk_probability", 0)
        max_savings = optimal_strategy.get("maximum_savings_potential", 0)
        alternatives = optimal_strategy.get("optimal_alternatives", [])

        # Format expense lines
        expense_lines = []
        for k, v in expense_breakdown.items():
            if k != "total_expenses":
                pct = round((v / total_exp * 100), 1) if total_exp > 0 else 0
                expense_lines.append(
                    f"  • {k.replace('_',' ').title()}: LKR {v:,.0f} ({pct}%)"
                )

        # Format current alternatives
        alt_lines = []
        for a in alternatives[:5]:
            alt_lines.append(
                f"  • {a.get('category','')}: '{a.get('current_choice','')}' → '{a.get('optimal_choice','')}' "
                f"(save LKR {a.get('estimated_savings',0):,.0f}/mo, {a.get('priority','')} priority)"
            )

        university = student_profile.get("university", "Sri Lankan university")
        district = student_profile.get("district", "Sri Lanka")
        year = student_profile.get("year_of_study", "a student")
        food_type = student_profile.get("food_type", "mixed")
        transport = student_profile.get("transport_method", "bus")
        field = student_profile.get("field_of_study", "studies")
        acc_type = student_profile.get("accommodation_type", "rented room")

        # Pull optimised target numbers
        current_exp = optimal_strategy.get("current_situation", {}).get(
            "total_expenses", total_exp
        )
        target_exp = optimal_strategy.get("optimal_target", {}).get(
            "target_expenses", current_exp
        )
        target_rate = optimal_strategy.get("optimal_target", {}).get(
            "target_savings_rate", savings_rate
        )
        gap = max(current_exp - target_exp, 0)

        # ── Enforce minimum savings buffer ─────────────────────────
        MIN_SAVINGS_BUFFER = 7500  # LKR — target must be at least 7,500 below income
        # The hard ceiling for expenses: income minus the minimum buffer
        income_ceiling = max(income - MIN_SAVINGS_BUFFER, 0)

        # Determine if student is over budget or needs the savings buffer enforced
        over_budget = total_exp > income_ceiling
        deficit = max(total_exp - income_ceiling, 0)
        # raw optimised target, but must always leave MIN_SAVINGS_BUFFER as savings
        raw_target = min(income_ceiling, target_exp)
        real_target = min(raw_target, income_ceiling)  # hard cap
        real_gap = max(total_exp - real_target, 0)  # how much to cut
        min_saving = income - real_target  # guaranteed saving

        # Build optimised-category estimates for FINAL_BUDGET guidance
        cat_optimised = {}
        for k, v in expense_breakdown.items():
            if k == "total_expenses":
                continue
            # Proportional reduction to hit real_target
            if total_exp > 0 and real_gap > 0:
                reduction = (v / total_exp) * real_gap
                cat_optimised[k] = max(round(v - reduction), 0)
            else:
                cat_optimised[k] = v

        final_budget_lines = []
        for k, v in cat_optimised.items():
            final_budget_lines.append(f"  • {k.replace('_',' ').title()}: LKR {v:,.0f}")

        constraint_note = (
            f"⚠️  CRITICAL: Student is OVER the safe-spend ceiling by LKR {deficit:,.0f}/month. "
            f"Steps MUST reduce total expenses to ≤ LKR {income_ceiling:,.0f} "
            f"so at least LKR {MIN_SAVINGS_BUFFER:,.0f} is saved each month."
            if over_budget
            else f"Student is within income. Still, steps MUST optimise expenses to ≤ LKR {real_target:,.0f}/month "
            f"guaranteeing at least LKR {min_saving:,.0f} monthly savings "
            f"(LKR {MIN_SAVINGS_BUFFER:,.0f} minimum buffer enforced)."
        )

        prompt = f"""You are an expert financial coach for Sri Lankan university students.
A student used our AI Budget Optimizer. Generate a precise numbered step-by-step plan showing EXACTLY how to bring ALL monthly expenses WITHIN their income limit.

─── STUDENT ────────────────────────────────────────────────
University: {university} | Year: {year} | Field: {field}
District: {district} | Accommodation: {acc_type}
Food: {food_type} | Transport: {transport}

─── INCOME vs EXPENSE CONSTRAINT ───────────────────────────
Monthly Income         : LKR {income:,.0f}
Safe-Spend Ceiling     : LKR {income_ceiling:,.0f}  ← expenses MUST be ≤ this (income − LKR {MIN_SAVINGS_BUFFER:,.0f} buffer)
Minimum Monthly Saving : LKR {MIN_SAVINGS_BUFFER:,.0f}  ← this gap must ALWAYS remain between expenses and income
Current Expenses       : LKR {current_exp:,.0f}
Gap to Close           : LKR {real_gap:,.0f}
Optimised Target       : LKR {real_target:,.0f}/month  (saves LKR {min_saving:,.0f})
Target Savings Rate    : {target_rate}%

{constraint_note}

─── CURRENT EXPENSE BREAKDOWN ──────────────────────────────
{chr(10).join(expense_lines)}

─── AI-SUGGESTED OPTIMISED BUDGET ──────────────────────────
{chr(10).join(final_budget_lines)}
  ─────────────────────────────────────────────────────
  TOTAL after optimising : LKR {real_target:,.0f}
  Monthly Savings        : LKR {min_saving:,.0f}  ✅  (≥ LKR {MIN_SAVINGS_BUFFER:,.0f} buffer achieved)

─── AI-IDENTIFIED ALTERNATIVES ─────────────────────────────
{chr(10).join(alt_lines) if alt_lines else '  • No critical alternatives flagged'}

─── OUTPUT FORMAT ───────────────────────────────────────────
Use EXACTLY this structure. NO extra text outside this format.

GAP_SUMMARY: By reducing expenses by LKR {real_gap:,.0f}/month you will always have at least LKR {MIN_SAVINGS_BUFFER:,.0f} left over — here is how to do it in [X] steps.

STEP 1: [Short action title — keep it practical, Sri Lanka specific]
CATEGORY: [Food / Transport / Accommodation / Internet / Utilities / Study / Entertainment / Income]
SAVE: LKR [amount]/month
HOW: [One practical sentence — use Sri Lanka context: CTB buses, Keells/Cargills, student ID, BOC/NSB]
TIMEFRAME: [This week / Week 2 / Week 3 / Month 2 / Month 3]

STEP 2: [title]
CATEGORY: [...]
SAVE: LKR [amount]/month
HOW: [...]
TIMEFRAME: [...]

[Add STEP 3 to STEP 5 in the same format. SAVE amounts across all steps must total LKR {real_gap:,.0f}.]

FINAL_BUDGET: After applying all steps — Food: LKR [X] | Transport: LKR [X] | Accommodation: LKR [X] | Other: LKR [X] | TOTAL: LKR [X] | SAVINGS: LKR [X] | FITS WITHIN INCOME: YES

QUICK_WIN: [One thing doable TODAY for free that immediately saves money]

MOTIVATION: [One encouraging sentence — mention income LKR {income:,.0f}, new total LKR {real_target:,.0f}, and that LKR {min_saving:,.0f} will be saved every month]

─── STRICT RULES ────────────────────────────────────────────
1. TOTAL in FINAL_BUDGET must be ≤ LKR {income_ceiling:,.0f} — this is non-negotiable
2. SAVINGS in FINAL_BUDGET must be ≥ LKR {MIN_SAVINGS_BUFFER:,.0f} — there must always be a visible gap between expenses and income
3. SAVE amounts across all steps must sum to LKR {real_gap:,.0f}
4. Use "you/your" throughout, keep tone encouraging yet realistic
5. Reference Sri Lanka specifics in every HOW field
6. Output ONLY the structured format above — NOTHING outside these fields"""

        # ── Call OpenAI API ────────────────────────────────────────
        success, content, error_msg = call_openai_with_retry(OPENAI_API_KEY, prompt)

        if success:
            # Cache the successful response
            cache_openai_response(cache_key, content)

            return jsonify(
                {
                    "success": True,
                    "ai_strategy": content,
                    "ai_provider": "OpenAI",
                    "cached": False,
                    "prompt_data": {
                        "income": income,
                        "total_expenses": total_exp,
                        "savings_rate": savings_rate,
                        "risk_level": risk_level,
                        # AI-computed constraint numbers — used by the frontend
                        # Budget Transformation card so it shows identical figures
                        "income_ceiling": income_ceiling,
                        "real_target": real_target,
                        "real_gap": real_gap,
                        "min_saving": min_saving,
                        "min_savings_buffer": MIN_SAVINGS_BUFFER,
                        "current_expenses": current_exp,
                        "target_rate": target_rate,
                    },
                    "timestamp": datetime.now().isoformat(),
                }
            )
        else:
            # OpenAI failed
            is_rate_limit = (
                "rate limit" in error_msg.lower() or "quota" in error_msg.lower()
            )

            return jsonify(
                {
                    "success": False,
                    "error": (
                        "OpenAI service unavailable"
                        if not is_rate_limit
                        else "OpenAI rate limit"
                    ),
                    "user_message": (
                        "The AI service is temporarily busy. Your budget analysis is complete - the AI insights will be available shortly. Please try again in a few minutes."
                        if is_rate_limit
                        else "Could not generate AI insights, but your budget analysis is complete."
                    ),
                    "technical_details": error_msg,
                    "retry_suggested": True,
                }
            ), (429 if is_rate_limit else 502)

    except Exception as e:
        print(f"❌ AI strategy error: {e}")
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Internal server error",
                    "user_message": "An error occurred while generating AI insights.",
                    "technical_details": str(e),
                }
            ),
            500,
        )


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5002"))
    print("\n" + "=" * 60)
    print("🎯 AI-Powered Student Budget Optimizer API")
    print("=" * 60)
    print(f"📍 Server: http://127.0.0.1:{port}")
    print(f"📍 Health: http://127.0.0.1:{port}/health")
    if cors_origins == "*":
        cors_label = "all origins"
    else:
        cors_label = ", ".join(cors_origins)
    print(f"📍 CORS: {cors_label}")
    print("=" * 60 + "\n")

    app.run(debug=True, port=port, host="0.0.0.0")
