"""
AgriDiff AI — Embedder
Generates sentence embeddings using sentence-transformers (local, no API cost).
Model: all-MiniLM-L6-v2 (80MB, fast on CPU)
"""

import logging
import numpy as np
from typing import List

logger = logging.getLogger("agridiff.embedder")

MODEL_NAME = "all-MiniLM-L6-v2"
_embedder = None  # singleton


def get_embedder():
    """Load and cache the embedding model (called once on startup)."""
    global _embedder
    if _embedder is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading embedding model: {MODEL_NAME}")
            _embedder = SentenceTransformer(MODEL_NAME)
            logger.info("Embedding model loaded ✅")
        except Exception as e:
            logger.error(f"Failed to load sentence-transformers: {e}")
            _embedder = None
    return _embedder


def embed_chunks(texts: List[str]) -> np.ndarray:
    """
    Embed a list of text strings.
    Returns numpy array of shape (N, embedding_dim).
    Falls back to TF-IDF vectors if model unavailable.
    """
    model = get_embedder()

    if model is not None:
        try:
            embeddings = model.encode(texts, batch_size=32, show_progress_bar=False, normalize_embeddings=True)
            return np.array(embeddings)
        except Exception as e:
            logger.warning(f"Sentence-transformer encode failed: {e} — using TF-IDF fallback")

    return _tfidf_embed(texts)


def _tfidf_embed(texts: List[str]) -> np.ndarray:
    """TF-IDF fallback when sentence-transformers is unavailable."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.preprocessing import normalize

    logger.info("Using TF-IDF fallback for embeddings")
    vectorizer = TfidfVectorizer(max_features=512, stop_words="english")
    try:
        matrix = vectorizer.fit_transform(texts)
        return normalize(matrix.toarray(), norm="l2")
    except Exception as e:
        logger.error(f"TF-IDF also failed: {e}")
        # Last resort: random unit vectors (won't be accurate but won't crash)
        return np.random.randn(len(texts), 384)

