from app.domain.student import StudentProfile
from app.pipelines.recommendation_pipeline import RecommendationPipeline

pipeline = RecommendationPipeline()

student = StudentProfile(
    stream="Physical Science",
    subjects=["Combined Mathematics", "Physics", "Chemistry"],
    zscore=1.8,
    interests="doctor surgeon medical hospital healthcare",
)

# This will trigger 0 matches because the similarity score for 'doctor' will be extremely low for physical science degrees (like computer science, math, physics).
res = pipeline.recommend(student, "Colombo")

print("---")
print("Eligible:", len(res["eligible_recommendations"]))
print("Global Explanation:")
print(res.get("summary", {}).get("global_explanation"))
