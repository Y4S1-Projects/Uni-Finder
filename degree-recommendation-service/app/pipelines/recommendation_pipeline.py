# app/pipelines/recommendation_pipeline.py
from typing import List, Dict, Optional
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
        self.embeddings = None
        try:
            self.embeddings = np.load(EMBEDDINGS_PATH)
        except Exception:
            # Embeddings are an optimization; fall back to on-the-fly similarity.
            self.embeddings = None

    def recommend(
        self,
        student: StudentProfile,
        district: str,
        max_results: Optional[int] = None,
    ) -> List[Dict]:
        debug = self.recommend_debug(
            student=student, district=district, max_results=max_results
        )
        eligible = debug["eligible_recommendations"]
        # Strip explanation-heavy fields for the simple endpoint.
        for item in eligible:
            item.pop("reason", None)
            item.pop("subjects_required", None)
            item.pop("stream_required", None)
            item.pop("student_subjects", None)
            item.pop("student_stream", None)
            item.pop("student_zscore", None)
            item.pop("district", None)
            item.pop("eligibility", None)
        return eligible

    def recommend_debug(
        self,
        student: StudentProfile,
        district: str,
        max_results: Optional[int] = None,
    ) -> Dict:
        programs = self.program_repo.get_all_programs()
        student_vec = self.similarity_engine.encode_text(student.interests)

        embeddings_ok = (
            self.embeddings is not None
            and isinstance(self.embeddings, np.ndarray)
            and len(self.embeddings) == len(programs)
        )

        eligible = []
        rejected = []

        for idx, program in enumerate(programs):
            is_eligible, reason = check_eligibility(student, program, district)

            if embeddings_ok:
                similarity = float(
                    self.similarity_engine.compute_similarity_vectors(
                        student_vec,
                        self.embeddings[idx],
                    )
                )
            else:
                similarity = float(
                    self.similarity_engine.compute_similarity(
                        student.interests,
                        program.degree_name,
                    )
                )

            debug_entry = {
                "degree_name": program.degree_name,
                "stream_required": program.stream,
                "subjects_required": program.subject_prerequisites,
                "metadata": program.metadata,
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

        eligible_recommendations = (
            eligible if max_results is None else eligible[:max_results]
        )

        return {
            "eligible_recommendations": eligible_recommendations,
            "rejected_programs": rejected,
            "summary": {
                "total_programs": len(programs),
                "eligible_count": len(eligible),
                "rejected_count": len(rejected),
            },
        }
