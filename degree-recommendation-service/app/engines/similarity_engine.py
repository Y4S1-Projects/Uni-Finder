# app/engines/similarity_engine.py
import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.utils.math_utils import cosine_similarity


class SimilarityEngine:
    def __init__(self):
        self.model = _get_model(settings.EMBEDDING_MODEL_NAME)

    def encode_text(self, text: str) -> np.ndarray:
        return self.model.encode(text, normalize_embeddings=True)

    def compute_similarity_vectors(
        self,
        student_vec: np.ndarray,
        program_vec: np.ndarray,
    ) -> float:
        # When embeddings are normalized, cosine similarity == dot product.
        if student_vec is None or program_vec is None:
            return 0.0
        return float(np.dot(student_vec, program_vec))

    def compute_similarity(self, student_interests: str, program_text: str) -> float:
        student_vec = self.encode_text(student_interests)
        program_vec = self.encode_text(program_text)

        return cosine_similarity(student_vec, program_vec)


_MODEL_CACHE: dict[str, SentenceTransformer] = {}


def _get_model(model_name: str) -> SentenceTransformer:
    model = _MODEL_CACHE.get(model_name)
    if model is None:
        model = SentenceTransformer(model_name)
        _MODEL_CACHE[model_name] = model
    return model
