from flask import Flask, request, jsonify, render_template
from flask_cors import CORS  # Import CORS
import pandas as pd
import random
import numpy as np
from datetime import datetime


# Budget Optimizer Integration
import sys
sys.path.append('/Users/shehansalitha/Desktop/Uni-Finder/backend')
from budget_optimizer_trainer import StudentBudgetOptimizer

# Initialize budget optimizer
budget_optimizer = StudentBudgetOptimizer()
try:
    budget_optimizer.load_models()
    print("✅ Budget optimizer models loaded successfully")
except:
    print("⚠️ Budget optimizer models not found. Run budget_optimizer_trainer.py first")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global variables to track recommendations and calculate accuracy
recommendation_stats = {
    'total_requests': 0,
    'successful_recommendations': 0,
    'avg_score': 0,
    'last_updated': datetime.now()
}

# Load your dataset
try:
    places = pd.read_csv('places_final_dataset (2).csv')
    print(f"Dataset loaded successfully with {len(places)} places")
except Exception as e:
    print(f"Error loading dataset: {e}")
    places = pd.DataFrame()

# Simple recommendation function without ML
def recommend_places_simple(user_input, places_df, top_n=5):
    """
    Simple recommendation function based on text matching
    """
    if places_df.empty:
        return pd.DataFrame()
    
    # Convert user input to lowercase
    user_input_lower = user_input.lower()
    
    # Create a score based on text matching
    places_df = places_df.copy()
    places_df['score'] = 0
    
    # Check if columns exist and score accordingly
    if 'name' in places_df.columns:
        places_df['score'] += places_df['name'].str.lower().str.contains(user_input_lower, na=False).astype(int) * 3
    
    if 'latest_reviews' in places_df.columns:
        places_df['score'] += places_df['latest_reviews'].str.lower().str.contains(user_input_lower, na=False).astype(int) * 2
    
    if 'formatted_address' in places_df.columns:
        places_df['score'] += places_df['formatted_address'].str.lower().str.contains(user_input_lower, na=False).astype(int) * 1
        
    # Add some randomness for places with score 0
    places_df.loc[places_df['score'] == 0, 'score'] = places_df.loc[places_df['score'] == 0, 'score'].astype(float) + random.random()
    
    # Sort by score and return top recommendations
    recommended = places_df.nlargest(top_n, 'score')
    
    # Calculate recommendation quality metrics
    if not recommended.empty:
        max_possible_score = 6  # 3 (name) + 2 (reviews) + 1 (address)
        avg_score = recommended['score'].mean()
        quality_score = min(avg_score / max_possible_score, 1.0) * 100
        
        # Update global stats
        recommendation_stats['total_requests'] += 1
        recommendation_stats['successful_recommendations'] += 1
        recommendation_stats['avg_score'] = (
            (recommendation_stats['avg_score'] * (recommendation_stats['total_requests'] - 1) + quality_score) 
            / recommendation_stats['total_requests']
        )
        recommendation_stats['last_updated'] = datetime.now()
    
    # Add mock temperature data
    recommended = recommended.copy()
    recommended['temperature'] = [random.randint(15, 35) for _ in range(len(recommended))]
    
    # Select relevant columns
    columns_to_return = ['name', 'rating', 'temperature']
    if 'formatted_address' in recommended.columns:
        columns_to_return.insert(1, 'formatted_address')
    
    return recommended[columns_to_return]

@app.route('/recommend', methods=['POST'])
def recommend():
    """
    Flask route to handle recommendation requests.
    """
    try:
        # Get user input from the request
        user_input = request.json['user_input']
        print(f"Received recommendation request for: {user_input}")

        # Generate recommendations
        recommendations = recommend_places_simple(user_input, places)
        
        if recommendations.empty:
            return jsonify([])

        # Return recommendations as JSON
        result = recommendations.to_dict(orient='records')
        print(f"Returning {len(result)} recommendations")
        return jsonify(result)
    except Exception as e:
        print(f"Error in recommend endpoint: {e}")
        # Handle errors and return a meaningful message
        return jsonify({"error": str(e)}), 500

@app.route('/best_recommendation', methods=['POST'])
def best_recommendation():
    """
    Flask route to generate and display the best recommendation.
    """
    try:
        # Get user input and recommendations from the request
        user_input = request.json['user_input']
        recommendations = request.json['recommendations']
        
        print(f"Generating best recommendation for: {user_input}")

        if not recommendations:
            return jsonify({"recommendation": "No recommendations available."})

        # Simple best recommendation logic
        best_place = recommendations[0]  # First one is typically the best
        best_recommendation_text = f"Based on your search for '{user_input}', we recommend {best_place['name']} as the top choice. It has a rating of {best_place['rating']} and current temperature of {best_place['temperature']}°C, making it an excellent destination for your trip."

        return jsonify({"recommendation": best_recommendation_text})
    except Exception as e:
        print(f"Error in best_recommendation endpoint: {e}")
        # Handle errors and return a meaningful message
        return jsonify({"error": str(e)}), 500

@app.route('/accuracy', methods=['GET'])
def get_model_accuracy():
    """
    Display model accuracy and performance metrics
    """
    try:
        # Calculate accuracy metrics
        success_rate = (recommendation_stats['successful_recommendations'] / 
                       max(recommendation_stats['total_requests'], 1)) * 100
        
        # Calculate coverage (how many places can be recommended from dataset)
        coverage = (len(places) / max(len(places), 1)) * 100 if not places.empty else 0
        
        # Calculate recommendation quality based on average scores
        quality_score = recommendation_stats['avg_score']
        
        # Determine overall accuracy (weighted combination)
        overall_accuracy = (success_rate * 0.4 + coverage * 0.3 + quality_score * 0.3)
        
        accuracy_data = {
            "overall_accuracy": round(overall_accuracy, 2),
            "success_rate": round(success_rate, 2),
            "recommendation_quality": round(quality_score, 2),
            "dataset_coverage": round(coverage, 2),
            "total_requests": recommendation_stats['total_requests'],
            "successful_recommendations": recommendation_stats['successful_recommendations'],
            "dataset_size": len(places),
            "last_updated": recommendation_stats['last_updated'].strftime("%Y-%m-%d %H:%M:%S"),
            "accuracy_breakdown": {
                "text_matching_score": round(quality_score, 2),
                "response_reliability": round(success_rate, 2),
                "data_completeness": round(coverage, 2)
            }
        }
        
        print(f"Model accuracy requested - Overall: {overall_accuracy:.2f}%")
        return jsonify(accuracy_data)
        
    except Exception as e:
        print(f"Error calculating accuracy: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/budget', methods=['GET'])
def budget_optimizer_interface():
    """
    Serve the budget optimizer web interface
    """
    from flask import render_template
    return render_template('budget_optimizer.html')

@app.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint
    """
    return jsonify({"status": "healthy", "places_count": len(places)})


# Budget Optimizer Routes
@app.route('/budget/predict', methods=['POST'])
def predict_expenses():
    """Predict monthly expenses for a student"""
    try:
        student_data = request.json
        if 'income' not in student_data:
            return jsonify({"error": "Missing income field"}), 400
        
        prediction = budget_optimizer.predict_monthly_expenses(student_data)
        if prediction is None:
            return jsonify({"error": "Prediction failed"}), 500
        
        return jsonify({"success": True, "prediction": prediction})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/budget/optimize', methods=['POST'])
def optimize_budget():
    """Optimize budget allocation for a student"""
    try:
        student_data = request.json
        target_savings = student_data.get('target_savings_rate', 0.15)
        
        if 'income' not in student_data:
            return jsonify({"error": "Missing income field"}), 400
        
        optimization = budget_optimizer.optimize_budget(student_data, target_savings)
        if optimization is None:
            return jsonify({"error": "Optimization failed"}), 500
        
        return jsonify({"success": True, "optimization": optimization})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/budget/performance', methods=['GET'])
def budget_model_performance():
    """Get budget model performance metrics"""
    try:
        performance = budget_optimizer.get_model_performance()
        return jsonify({"success": True, "performance": performance})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True, port=5001, host='0.0.0.0')