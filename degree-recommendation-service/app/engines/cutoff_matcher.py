# app/engines/cutoff_matcher.py
import numpy as np
from app.engines.similarity_engine import SimilarityEngine
from app.repositories.cutoff_repository import CutoffRepository


class CutoffMatcher:
    def __init__(self):
        self.similarity_engine = SimilarityEngine()
        self.cutoff_repo = CutoffRepository()

        # Load cutoff data once
        self.cutoff_repo.load()

        # Unique program names in cutoff dataset
        self.cutoff_names = list(
            set(name for (name, _) in self.cutoff_repo._cache.keys())
        )

        # Precompute embeddings
        self.cutoff_vectors = [
            self.similarity_engine.encode_text(name) for name in self.cutoff_names
        ]

    def get_cutoff_semantic(
        self, program_name: str, district: str, threshold: float = 0.85
    ):
        query_vec = self.similarity_engine.encode_text(program_name)

        scores = [float(np.dot(query_vec, vec)) for vec in self.cutoff_vectors]

        best_idx = int(np.argmax(scores))
        best_score = scores[best_idx]

        if best_score < threshold:
            return None, f"No semantic match (confidence={best_score:.2f})"

        matched_name = self.cutoff_names[best_idx]
        cutoff = self.cutoff_repo.get_cutoff(matched_name, district)

        if cutoff is None:
            return (
                None,
                f"Matched '{matched_name}' but no cutoff for district {district}",
            )

        return cutoff, f"Matched '{matched_name}' (confidence={best_score:.2f})"
