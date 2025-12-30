# app/pipelines/recommendation_pipeline.py
from typing import List, Dict
import numpy as np

from app.domain.student import StudentProfile
from app.engines.rules_engine import check_eligibility
from app.engines.similarity_engine import SimilarityEngine
from app.engines.ranking_engine import RankingEngine
from app.repositories.program_repository import ProgramRepository
from app.core.paths import EMBEDDINGS_PATH


class RecommendationPipeline:
    def __init__(self):
        self.program_repo = ProgramRepository()
        self.similarity_engine = SimilarityEngine()
        self.ranking_engine = RankingEngine()
        self.embeddings = np.load(EMBEDDINGS_PATH)

    def recommend_debug(
        self,
        student: StudentProfile,
        district: str,
        max_results: int = 5,
    ) -> Dict:
        programs = self.program_repo.get_all_programs()
        student_vec = self.similarity_engine.encode_text(student.interests)

        eligible = []
        rejected = []

        for idx, program in enumerate(programs):
            is_eligible, reason = check_eligibility(student, program, district)

            similarity = float(
                self.similarity_engine.compute_similarity(
                    student.interests, program.degree_name
                )
            )

            debug_entry = {
                "degree_name": program.degree_name,
                "stream_required": program.stream,
                "subjects_required": program.subject_prerequisites,
                "student_stream": student.stream,
                "student_subjects": student.subjects,
                "student_zscore": student.zscore,
                "district": district,
                "similarity": round(similarity, 4),
                "eligibility": is_eligible,
                "reason": reason,
            }

            if is_eligible:
                score = self.ranking_engine.score(is_eligible, similarity)
                debug_entry["score"] = score
                eligible.append(debug_entry)
            else:
                rejected.append(debug_entry)

        eligible.sort(key=lambda x: x["score"], reverse=True)

        return {
            "eligible_recommendations": eligible[:max_results],
            "rejected_programs": rejected,
            "summary": {
                "total_programs": len(programs),
                "eligible_count": len(eligible),
                "rejected_count": len(rejected),
            },
        }
