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
        above_score_count: int = 0,
    ) -> List[Dict]:
        debug = self.recommend_debug(
            student=student,
            district=district,
            max_results=max_results,
            above_score_count=above_score_count,
        )

        # Combine eligible and above-score recommendations
        all_recommendations = debug["eligible_recommendations"] + debug.get(
            "above_score_recommendations", []
        )

        # Strip explanation-heavy fields for the simple endpoint.
        for item in all_recommendations:
            item.pop("reason", None)
            item.pop("subjects_required", None)
            item.pop("stream_required", None)
            item.pop("student_subjects", None)
            item.pop("student_stream", None)
            item.pop("student_zscore", None)
            item.pop("district", None)
            item.pop("eligibility_details", None)
            # Keep eligibility flag to distinguish eligible vs above-score

        return all_recommendations

    def recommend_debug(
        self,
        student: StudentProfile,
        district: str,
        max_results: Optional[int] = None,
        above_score_count: int = 0,
    ) -> Dict:
        programs = self.program_repo.get_all_programs()
        student_vec = self.similarity_engine.encode_text(student.interests)

        embeddings_ok = (
            self.embeddings is not None
            and isinstance(self.embeddings, np.ndarray)
            and len(self.embeddings) == len(programs)
        )

        eligible = []
        above_score = []  # Courses above student's z-score
        rejected = []

        for idx, program in enumerate(programs):
            # Updated to handle new check_eligibility return signature
            is_eligible, reason, details = check_eligibility(student, program, district)

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
                        program.course_name,
                    )
                )

            debug_entry = {
                "course_code": program.course_code,
                "course_name": program.course_name,
                "degree_name": program.course_name,  # Backwards compatibility
                "stream_required": program.stream,
                "subjects_required": program.subject_requirements,
                "universities": program.universities,
                "faculty_department": program.faculty_department,
                "duration": program.duration,
                "degree_programme": program.degree_programme,
                "medium_of_instruction": program.medium_of_instruction,
                "practical_test": program.practical_test,
                "proposed_intake": program.proposed_intake,
                "notes": program.notes,
                "metadata": program.metadata,
                "student_stream": student.stream,
                "student_subjects": student.subjects,
                "student_zscore": student.zscore,
                "district": district,
                "similarity": round(similarity, 4),
                "eligibility": is_eligible,
                "reason": reason,
                "eligibility_details": details,
            }

            if is_eligible:
                score = self.ranking_engine.score(is_eligible, similarity)
                debug_entry["score"] = score
                eligible.append(debug_entry)
            else:
                # Check if rejection was due to z-score (aspirational course)
                if (
                    details.get("zscore_check") == False
                    and details.get("stream_match")
                    and details.get("subject_match")
                ):
                    # This is a course the student could reach with higher z-score
                    score = self.ranking_engine.score(False, similarity)
                    debug_entry["score"] = score
                    debug_entry["aspirational"] = True
                    above_score.append(debug_entry)
                else:
                    rejected.append(debug_entry)

        # Sort eligible by score
        eligible.sort(key=lambda x: x["score"], reverse=True)

        # Sort above-score by similarity (most relevant first)
        above_score.sort(key=lambda x: x["similarity"], reverse=True)

        # Apply limits
        eligible_recommendations = (
            eligible if max_results is None else eligible[:max_results]
        )

        above_score_recommendations = (
            above_score[:above_score_count] if above_score_count > 0 else []
        )

        return {
            "eligible_recommendations": eligible_recommendations,
            "above_score_recommendations": above_score_recommendations,
            "rejected_programs": rejected,
            "summary": {
                "total_programs": len(programs),
                "eligible_count": len(eligible),
                "above_score_count": len(above_score_recommendations),
                "rejected_count": len(rejected),
            },
        }
