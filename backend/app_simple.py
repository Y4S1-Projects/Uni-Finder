from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import pandas as pd
import random

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

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

@app.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint
    """
    return jsonify({"status": "healthy", "places_count": len(places)})

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True, port=5001, host='0.0.0.0')