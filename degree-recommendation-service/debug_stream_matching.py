"""Debug script to see what courses match software engineer query"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.ol_pathway_service import OLPathwayService
from app.repositories.course_recommendation_repository import (
    CourseRecommendationRepository,
)
from app.engines.similarity_engine import SimilarityEngine
from app.engines.explanation_engine import ExplanationEngine

# Initialize service
course_repo = CourseRecommendationRepository()
similarity_engine = SimilarityEngine()
explanation_engine = ExplanationEngine()
service = OLPathwayService(course_repo, similarity_engine, explanation_engine)

# Test query
student_input = "I want to become a software engineer and build applications"

# Get target degrees
target_degrees = service._find_target_degrees(student_input, 10)

print(f"Query: {student_input}\n")
print(f"Top {len(target_degrees)} Matching Degrees:")
print("=" * 80)

for i, degree in enumerate(target_degrees, 1):
    print(f"{i}. {degree.course_name} (Code: {degree.course_code})")
    print(f"   Stream: {degree.stream}")
    print(f"   Match: {degree.match_score_percentage}%")
    print(f"   Careers: {', '.join(degree.job_roles[:3])}")
    print()

# Show stream distribution
from collections import Counter

stream_counts = Counter([d.stream for d in target_degrees])
print("\nStream Distribution:")
for stream, count in stream_counts.most_common():
    print(f"  {stream}: {count} courses")

# Extract recommended stream
recommended_stream, confidence = service._extract_recommended_stream(target_degrees)
print(f"\nRecommended Stream: {recommended_stream} ({confidence}% confidence)")
