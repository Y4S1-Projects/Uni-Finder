# scripts/generate_embeddings.py
import numpy as np
import pandas as pd

from sentence_transformers import SentenceTransformer
from app.core.paths import PROGRAM_CATALOG_PATH, EMBEDDINGS_PATH
from app.core.config import settings


def main():
    # Load program catalog
    df = pd.read_csv(PROGRAM_CATALOG_PATH)

    # Validate required column
    if "degree_name" not in df.columns:
        raise ValueError(
            f"'degree_name' column not found in program catalog. "
            f"Available columns: {list(df.columns)}"
        )

    # Use ONLY degree_name for embeddings
    texts = df["degree_name"].fillna("").astype(str).tolist()

    # Load SBERT model
    model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)

    # Generate embeddings
    embeddings = model.encode(texts, normalize_embeddings=True)

    # Save embeddings
    np.save(EMBEDDINGS_PATH, embeddings)

    print(f"✅ Saved {len(embeddings)} embeddings to {EMBEDDINGS_PATH}")


if __name__ == "__main__":
    main()
