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
import requests

# Import our custom modules
from budget_calculator import BudgetCalculator
from ml_budget_predictor import MLBudgetPredictor

app = Flask(__name__)
CORS(app)

# Initialize components
calculator = BudgetCalculator()
ml_predictor = MLBudgetPredictor()

# Global variables
DATA_DIR = "budget_optimizer_files"
MONGODB_API_URL = os.getenv(
    "MONGODB_API_URL", "http://localhost:8080/api/budget/save"
)  # Node.js MongoDB API

print("🚀 Budget Optimizer API Starting...")
print("=" * 60)


def save_to_mongodb(prediction_data):
    """
    Save budget prediction to MongoDB via Node.js API
    """
    try:
        response = requests.post(
            MONGODB_API_URL,
            json=prediction_data,
            headers={"Content-Type": "application/json"},
        )

        if response.status_code == 201:
            result = response.json()
            print(
                f"💾 Successfully saved to MongoDB - ID: {result.get('predictionId')}"
            )
            return result
        else:
            print(f"⚠️ Failed to save to MongoDB: {response.status_code}")
            print(f"   Response: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"⚠️ MongoDB save error: {e}")
        print(f"   Make sure the API gateway is running on port 8080")
        return None


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
            "transport_method_home": data.get("transport_method_home", "Bus"),
        }

        transport_budget = calculator.calculate_transport_budget(transport_data)
        print(f"✅ Transport Budget: LKR {transport_budget['monthly_total']}")

        # Step 3: Prepare student data for ML prediction
        student_data = {
            "monthly_income": data.get("monthly_income", 25000),
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

        monthly_income = data.get("monthly_income", 25000)
        calculated_savings = monthly_income - calculated_total_expenses
        savings_rate = (calculated_savings / monthly_income * 100) if monthly_income > 0 else 0
        
        # Step 5.5: Generate Optimal Budget Strategy (NEW FEATURE!)
        current_expense_breakdown = {
            'rent': rent,
            'food': food_budget['monthly_total'],
            'transport': transport_budget['monthly_total'],
            'internet': internet,
            'study_materials': study_materials,
            'entertainment': entertainment,
            'utilities': utilities,
            'healthcare': healthcare,
            'other': other,
            'total_expenses': calculated_total_expenses
        }
        
        optimal_strategy = ml_predictor.generate_optimal_budget_strategy(
            student_data, 
            current_expense_breakdown
        )
        print(f"✅ Optimal Strategy Generated - Potential Savings: LKR {optimal_strategy['maximum_savings_potential']}")
        
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
                "total_expenses": round(calculated_total_expenses, 2),
                "monthly_savings": round(calculated_savings, 2),
                "savings_rate": round(savings_rate, 1),
            },
            # ML predictions
            "ml_prediction": complete_analysis.get("budget_prediction"),
            "risk_assessment": complete_analysis.get("risk_assessment"),
            # Overall recommendation
            "recommendation": complete_analysis.get('recommendation'),
            "optimization_status": complete_analysis['financial_summary'].get('optimization_status'),
            
            # 🆕 NEW: Optimal Budget Strategy
            "optimal_strategy": optimal_strategy
        }

        print(f"✅ Complete analysis returned successfully")
        print(
            f"   Income: LKR {monthly_income} | Expenses: LKR {round(calculated_total_expenses, 2)} | Savings: LKR {round(calculated_savings, 2)}"
        )

        # Step 7: Save to MongoDB
        try:
            mongodb_data = {
                # User info (optional - can be passed from frontend)
                "userId": data.get("userId"),
                "username": data.get("username"),
                "email": data.get("email"),
                # Personal Information
                "monthly_income": monthly_income,
                "year_of_study": data.get("year_of_study", "Second Year"),
                "field_of_study": data.get("field_of_study", "IT"),
                "university": data.get("university", "SLIIT"),
                "district": data.get("district", "Colombo"),
                "accommodation_type": data.get("accommodation_type", "Rented Room"),
                # Budget Inputs
                "rent": rent,
                "internet": internet,
                "study_materials": study_materials,
                "entertainment": entertainment,
                "utilities": utilities,
                "healthcare": healthcare,
                "other": other,
                # Food Details
                "food_type": food_data["food_type"],
                "meals_per_day": food_data["meals_per_day"],
                "diet_type": food_data["diet_type"],
                "cooking_frequency": food_data["cooking_frequency"],
                "cooking_percentage": food_data.get("cooking_percentage", 0),
                "grocery_items": food_data.get("grocery_items", {}),
                "delivery_items": food_data.get("delivery_items", {}),
                # Transport Details
                "distance_uni_accommodation": transport_data[
                    "distance_uni_accommodation"
                ],
                "distance_home_uni": transport_data["distance_home_uni"],
                "transport_method": transport_data["transport_method"],
                "transport_method_home": transport_data["transport_method_home"],
                "days_per_week": transport_data["days_per_week"],
                "home_visit_frequency": transport_data["home_visit_frequency"],
                # Calculated Budgets
                "food_budget": {
                    "monthly_total": round(food_budget["monthly_total"], 2),
                    "breakdown": food_budget.get("breakdown", {}),
                    "recommendations": food_budget.get("recommendations", []),
                },
                "transport_budget": {
                    "monthly_total": round(transport_budget["monthly_total"], 2),
                    "breakdown": transport_budget.get("breakdown", {}),
                    "recommendations": transport_budget.get("recommendations", []),
                },
                # ML Prediction Results
                "predicted_budget": round(
                    complete_analysis.get("budget_prediction", {}).get(
                        "predicted_budget", 0
                    ),
                    2,
                ),
                "ml_confidence": round(
                    complete_analysis.get("budget_prediction", {}).get("confidence", 0)
                    * 100,
                    2,
                ),
                "risk_level": complete_analysis.get("risk_assessment", {}).get(
                    "risk_level", "Medium Risk"
                ),
                "risk_probability": round(
                    complete_analysis.get("risk_assessment", {}).get(
                        "risk_probability", 0
                    )
                    * 100,
                    2,
                ),
                # Financial Summary
                "total_expenses": round(calculated_total_expenses, 2),
                "calculated_savings": round(calculated_savings, 2),
                "savings_rate": round(savings_rate, 1),
                # Recommendations
                "recommendations": complete_analysis.get("recommendation", {}).get(
                    "key_recommendations", []
                ),
                "actionable_steps": complete_analysis.get("recommendation", {}).get(
                    "action_steps", []
                ),
                # Expense Breakdown
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
                },
                # Metadata
                "analysis_date": datetime.now().isoformat(),
                "status": "active",
            }

            # Save to MongoDB (non-blocking)
            mongo_result = save_to_mongodb(mongodb_data)
            if mongo_result:
                response["saved_to_db"] = True
                response["prediction_id"] = mongo_result.get("predictionId")
            else:
                response["saved_to_db"] = False

        except Exception as db_error:
            print(f"⚠️ Database save failed (continuing anyway): {db_error}")
            response["saved_to_db"] = False

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


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🎯 AI-Powered Student Budget Optimizer API")
    print("=" * 60)
    print("📍 Server: http://127.0.0.1:5002")
    print("📍 Health: http://127.0.0.1:5002/health")
    print("📍 CORS: Enabled for all origins")
    print("=" * 60 + "\n")

    app.run(debug=True, port=5002, host="0.0.0.0")
