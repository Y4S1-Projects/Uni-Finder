import os
import sys
import json
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.pipelines.recommendation_pipeline import RecommendationPipeline
from app.domain.student import StudentProfile

print("\n--- TEST 1: THE GIBBERISH TEST ---")
student_gibberish = StudentProfile(
    stream="Biological Science",
    subjects=["Biology", "Chemistry", "Physics"],
    zscore=1.5,
    interests="asdfghjkl",
)
pipeline = RecommendationPipeline()
response = pipeline.recommend(
    student=student_gibberish, district="COLOMBO", max_results=5
)

print(f"HTTP Status Code simulation: 200 OK")
if "summary" in response and "global_explanation" in response["summary"]:
    print(f"Global Explanation: {response['summary']['global_explanation']}")
else:
    print(f"Global Explanation: None found. Keys: {response.keys()}")

print("\n--- TEST 2: THE TIMEOUT TEST ---")

pipeline = RecommendationPipeline()


# Mock the Gemini call to raise TimeoutError
def mock_gemini_timeout(*args, **kwargs):
    raise TimeoutError("Gemini API is down or timing out")


pipeline._call_gemini_for_explanations = mock_gemini_timeout

# Valid student
student = StudentProfile(
    stream="Biological Science",
    subjects=["Biology", "Chemistry", "Physics"],
    zscore=1.85,
    interests="I want to be a doctor and help people.",
)

result = pipeline.recommend(student=student, district="COLOMBO", max_results=2)

print("Fallback Explanations Generated:")
for rec in result["eligible_recommendations"]:
    print(f"- Course: {rec['course_code']} | Explanation: {rec['explanation']}")
