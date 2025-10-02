
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS  # Import CORS
import pandas as pd
from sentence_transformers import SentenceTransformer, util
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import requests
import google.generativeai as genai  # Correct import for Gemini API

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Replace with your actual OpenWeatherMap API key
api_key = "7bd39690c587c11d168b63ca38997609"

# Load your dataset and model here
places = pd.read_csv('places_final_dataset (2).csv')

# Preprocess the dataset
def preprocess_data(places_df):
    """
    Preprocess the dataset to create necessary columns and normalize ratings.
    """
    # Clean text columns
    places_df['name'] = places_df['name'].apply(lambda x: x.lower().strip())
    places_df['latest_reviews'] = places_df['latest_reviews'].apply(lambda x: x.lower().strip())

    # Create a combined text field for embeddings
    places_df['text'] = places_df['name'] + " " + places_df['latest_reviews']

    # Normalize ratings and compute popularity score
    places_df[['rating', 'user_ratings_total']] = places_df[['rating', 'user_ratings_total']].fillna(0)
    scaler = MinMaxScaler()
    places_df[['norm_rating', 'norm_user_ratings_total']] = scaler.fit_transform(places_df[['rating', 'user_ratings_total']])
    places_df['popularity_score'] = places_df['norm_rating'] * places_df['norm_user_ratings_total']

    return places_df

# Preprocess the dataset
places = preprocess_data(places)

# Load the Sentence-BERT model
sbert_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Function to fetch current temperature using OpenWeatherMap API
def get_current_temperature(lat, lon, api_key):
    """
    Fetch the current temperature (in Celsius) using OpenWeatherMap API.
    """
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric"  # Use metric units for Celsius
    }
    try:
        print(f"Fetching temperature for lat={lat}, lon={lon}")  # Debugging
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        print(f"API response: {data}")  # Debugging
        # In the API response, the current temperature is found in data["main"]["temp"]
        return data["main"]["temp"]
    except Exception as e:
        print(f"Error fetching temperature for lat={lat}, lon={lon}: {e}")
        return None

# Define the recommendation function
def recommend_places_sbert(user_input, places_df, sbert_model, popularity_weight=0.3, top_n=5):
    """
    Recommend places using Sentence-BERT embeddings combined with a popularity score.
    For the final recommended places, fetch the current temperature using the OpenWeatherMap API.
    """
    # Clean and encode user input
    user_input_clean = user_input.lower().strip()
    user_embedding = sbert_model.encode(user_input_clean, convert_to_tensor=True)

    # Calculate cosine similarity for each place
    places_df['embedding'] = places_df['text'].apply(lambda x: sbert_model.encode(x, convert_to_tensor=True))
    similarities = places_df['embedding'].apply(lambda emb: util.cos_sim(user_embedding, emb).item())

    # Work on a copy to avoid modifying the original DataFrame
    df = places_df.copy()
    df['similarity'] = similarities

    # Compute final score: similarity + weighted popularity
    df['final_score'] = df['similarity'] + popularity_weight * df['popularity_score']

    # Select top recommendations based on final score
    recommended = df.nlargest(top_n, 'final_score').copy()

    # Fetch temperature only for these recommended places (if lat/lng columns exist)
    if "lat" in recommended.columns and "lng" in recommended.columns:
        print("Fetching temperatures for recommended places...")  # Debugging
        recommended["temperature"] = recommended.apply(
            lambda row: get_current_temperature(row["lat"], row["lng"], api_key), axis=1
        )
    else:
        print("lat and lng columns are missing in the dataset.")  # Debugging
        recommended["temperature"] = None

    return recommended[['name', 'formatted_address', 'rating', 'temperature', 'final_score']]

# Function to generate the best recommendation using Gemini API
def generate_best_recommendation(user_input, recommendations):
    """
    Generate the best recommendation using the Gemini API.
    """
    try:
        # Configure the Gemini API
        genai.configure(api_key="AIzaSyAZSfx4Ba01pnUFh0RxqOcYvzn0BYQ3ynw")

        # Initialize the Gemini model
        model = genai.GenerativeModel('gemini-2.0-flash')  # Use the correct model name

        # Generate the best recommendation
        prompt = f"Choose the top one place from {recommendations} for {user_input} and give the reason in one line."
        response = model.generate_content(prompt)

        # Debugging: Print the API response
        print(f"API Response: {response}")

        return response.text
    except Exception as e:
        print(f"Error generating best recommendation: {e}")
        return None

@app.route('/recommend', methods=['POST'])
def recommend():
    """
    Flask route to handle recommendation requests.
    """
    try:
        # Get user input from the request
        user_input = request.json['user_input']

        # Generate recommendations
        recommendations = recommend_places_sbert(user_input, places, sbert_model)

        # Return recommendations as JSON
        return jsonify(recommendations.to_dict(orient='records'))
    except Exception as e:
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

        # Generate the best recommendation using Gemini API
        best_recommendation_text = generate_best_recommendation(user_input, recommendations)

        # Return the best recommendation as JSON for the frontend to handle
        if best_recommendation_text:
            return jsonify({"recommendation": best_recommendation_text})
        else:
            # Fallback if Gemini API fails
            fallback_text = f"Based on your search for '{user_input}', we recommend {recommendations[0]['name']} as it has the highest rating and best overall score."
            return jsonify({"recommendation": fallback_text})
    except Exception as e:
        # Handle errors and return a meaningful message
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
