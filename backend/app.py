from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import os
import re
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import requests

# Optional heavy deps: service should still run without them.
try:
    from sentence_transformers import SentenceTransformer, util
except Exception:  # pragma: no cover
    SentenceTransformer = None
    util = None

try:
    import google.generativeai as genai  # Gemini API
except Exception:  # pragma: no cover
    genai = None

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY") or ""
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or ""

# Load dataset relative to this file (works regardless of cwd)
DATASET_PATH = os.getenv("PLACES_DATASET_PATH") or os.path.join(
    os.path.dirname(__file__), "places_final_dataset (2).csv"
)
places = pd.read_csv(DATASET_PATH)


# Preprocess the dataset
def preprocess_data(places_df):
    """
    Preprocess the dataset to create necessary columns and normalize ratings.
    """
    # Clean text columns
    places_df["name"] = places_df["name"].apply(lambda x: x.lower().strip())
    places_df["latest_reviews"] = places_df["latest_reviews"].apply(
        lambda x: x.lower().strip()
    )

    # Create a combined text field for embeddings
    places_df["text"] = places_df["name"] + " " + places_df["latest_reviews"]

    # Normalize ratings and compute popularity score
    places_df[["rating", "user_ratings_total"]] = places_df[
        ["rating", "user_ratings_total"]
    ].fillna(0)
    scaler = MinMaxScaler()
    places_df[["norm_rating", "norm_user_ratings_total"]] = scaler.fit_transform(
        places_df[["rating", "user_ratings_total"]]
    )
    places_df["popularity_score"] = (
        places_df["norm_rating"] * places_df["norm_user_ratings_total"]
    )

    return places_df


# Preprocess the dataset
places = preprocess_data(places)

# Load the Sentence-BERT model if available
sbert_model = None
if SentenceTransformer is not None:
    try:
        sbert_model = SentenceTransformer("paraphrase-MiniLM-L6-v2")
    except Exception as e:
        print(f"⚠️ SentenceTransformer unavailable, falling back to basic ranking: {e}")
        sbert_model = None


# Function to fetch current temperature using OpenWeatherMap API
def get_current_temperature(lat, lon, api_key):
    """
    Fetch the current temperature (in Celsius) using OpenWeatherMap API.
    """
    if not api_key:
        return None
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric",  # Use metric units for Celsius
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
def recommend_places_sbert(
    user_input, places_df, sbert_model, popularity_weight=0.3, top_n=5
):
    """
    Recommend places using Sentence-BERT embeddings combined with a popularity score.
    For the final recommended places, fetch the current temperature using the OpenWeatherMap API.
    """
    # Clean and encode user input
    user_input_clean = user_input.lower().strip()
    user_embedding = sbert_model.encode(user_input_clean, convert_to_tensor=True)

    # Calculate cosine similarity for each place
    places_df["embedding"] = places_df["text"].apply(
        lambda x: sbert_model.encode(x, convert_to_tensor=True)
    )
    similarities = places_df["embedding"].apply(
        lambda emb: util.cos_sim(user_embedding, emb).item()
    )

    # Work on a copy to avoid modifying the original DataFrame
    df = places_df.copy()
    df["similarity"] = similarities

    # Compute final score: similarity + weighted popularity
    df["final_score"] = df["similarity"] + popularity_weight * df["popularity_score"]

    # Select top recommendations based on final score
    recommended = df.nlargest(top_n, "final_score").copy()

    # Fetch temperature only for these recommended places (if lat/lng columns exist)
    if "lat" in recommended.columns and "lng" in recommended.columns:
        print("Fetching temperatures for recommended places...")  # Debugging
        recommended["temperature"] = recommended.apply(
            lambda row: get_current_temperature(row["lat"], row["lng"], api_key), axis=1
        )
    else:
        print("lat and lng columns are missing in the dataset.")  # Debugging
        recommended["temperature"] = None

    return recommended[
        ["name", "formatted_address", "rating", "temperature", "final_score"]
    ]


def _tokenize(text: str):
    return [t for t in re.split(r"[^a-z0-9]+", (text or "").lower()) if t]


def recommend_places_basic(user_input, places_df, top_n=5):
    """Fallback recommender when sentence-transformers isn't available."""
    tokens = set(_tokenize(user_input))
    df = places_df.copy()

    def score_row(row_text: str) -> float:
        row_tokens = set(_tokenize(row_text))
        if not tokens:
            return 0.0
        return float(len(tokens.intersection(row_tokens))) / float(len(tokens))

    df["similarity"] = df["text"].fillna("").apply(score_row)
    if "popularity_score" in df.columns:
        df["final_score"] = df["similarity"] + 0.3 * df["popularity_score"]
    else:
        df["final_score"] = df["similarity"]

    recommended = df.nlargest(top_n, "final_score").copy()
    if "lat" in recommended.columns and "lng" in recommended.columns:
        print("Fetching temperatures for recommended places...")
        recommended["temperature"] = recommended.apply(
            lambda row: get_current_temperature(
                row["lat"], row["lng"], OPENWEATHER_API_KEY
            ),
            axis=1,
        )
    else:
        recommended["temperature"] = None
    return recommended[
        ["name", "formatted_address", "rating", "temperature", "final_score"]
    ]


# Function to generate the best recommendation using Gemini API
def generate_best_recommendation(user_input, recommendations):
    """
    Generate the best recommendation using the Gemini API.
    """
    try:
        if genai is None or not GEMINI_API_KEY:
            return None

        # Configure the Gemini API
        genai.configure(api_key=GEMINI_API_KEY)

        # Initialize the Gemini model
        model = genai.GenerativeModel("gemini-2.0-flash")

        # Generate the best recommendation
        prompt = f"Choose the top one place from {recommendations} for {user_input} and give the reason in one line."
        response = model.generate_content(prompt)

        # Debugging: Print the API response
        print(f"API Response: {response}")

        return response.text
    except Exception as e:
        print(f"Error generating best recommendation: {e}")
        return None


@app.route("/recommend", methods=["POST"])
def recommend():
    """
    Flask route to handle recommendation requests.
    """
    try:
        # Get user input from the request
        user_input = request.json["user_input"]

        # Generate recommendations
        if sbert_model is not None and util is not None:
            recommendations = recommend_places_sbert(user_input, places, sbert_model)
        else:
            recommendations = recommend_places_basic(user_input, places)

        # Return recommendations as JSON
        return jsonify(recommendations.to_dict(orient="records"))
    except Exception as e:
        # Handle errors and return a meaningful message
        return jsonify({"error": str(e)}), 500


@app.route("/best_recommendation", methods=["POST"])
def best_recommendation():
    """
    Flask route to generate and display the best recommendation.
    """
    try:
        # Get user input and recommendations from the request
        user_input = request.json["user_input"]
        recommendations = request.json["recommendations"]

        # Generate the best recommendation using Gemini API
        best_recommendation_text = generate_best_recommendation(
            user_input, recommendations
        )

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


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5003"))
    app.run(debug=True, port=port, host="0.0.0.0")
