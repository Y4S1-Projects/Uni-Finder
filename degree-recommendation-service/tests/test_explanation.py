from app.domain.student import StudentProfile
from app.pipelines.recommendation_pipeline import RecommendationPipeline

pipeline = RecommendationPipeline()

student = StudentProfile(
    stream="Physical Science",
    subjects=["Combined Mathematics", "Physics", "Chemistry"],
    zscore=1.8,
    interests="i like business and mathematics",
)

# Dummy recommendation
recommendations = [
    {
        "course_code": "099",
        "course_name": "Software Engineering",
        "eligibility": True,
        "similarity": 0.85,
    }
]

explanations = pipeline._generate_explanations_batch(
    student, "Colombo", recommendations
)
print("EXPLANATION FOR 099:")
print(explanations.get("099", "No explanation generated."))
