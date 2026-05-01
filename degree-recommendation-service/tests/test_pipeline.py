import json
from app.pipelines.recommendation_pipeline import RecommendationPipeline
from app.domain.student import StudentProfile

pipeline = RecommendationPipeline()

student = StudentProfile(
    stream="Physical Science",
    subjects=[
        "Combined Mathematics",
        "Physics",
        "Information & Communication Technology",
    ],
    zscore=None,
    interests="software engineering",
)

debug_results = pipeline.recommend_debug(
    student=student, district="Colombo", max_results=15
)
results = debug_results["eligible_recommendations"]

print(f"Total eligible results: {len(results)}")
for r in results:
    print(
        f"[{r['course_code']}] {r['course_name']} - Eligible: {r['eligibility']} - Score: {r.get('score', 0):.4f}"
    )

rejected = debug_results.get("rejected_programs", [])
for r in rejected:
    if "Low relevance" in r.get("reason", ""):
        print(
            f"[REJECTED] [{r['course_code']}] {r['course_name']} - Reason: {r['reason']}"
        )
