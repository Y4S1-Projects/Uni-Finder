# app/engines/similarity_engine.py
import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.utils.math_utils import cosine_similarity


class SimilarityEngine:
    def __init__(self):
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)

    def encode_text(self, text: str) -> np.ndarray:
        return self.model.encode(text, normalize_embeddings=True)

    def compute_similarity(
        self,
        student_interests: str,
        program_text: str
    ) -> float:
        student_vec = self.encode_text(student_interests)
        program_vec = self.encode_text(program_text)

        return cosine_similarity(student_vec, program_vec)
