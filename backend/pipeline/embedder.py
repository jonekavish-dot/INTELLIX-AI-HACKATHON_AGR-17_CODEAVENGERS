"""
AgriDiff AI — Embedder
Generates semantic embeddings using sentence-transformers (local)
or a unified joint TF-IDF/Hashing vectorizer fallback.
BIT-AI-001 | AGR-17 | Team CODEAVENGERS
"""

import logging
import numpy as np
from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

logger = logging.getLogger("agridiff.embedder")

MODEL_NAME = "all-MiniLM-L6-v2"
_embedder = None  # singleton


def get_embedder():
    """Load and cache the embedding model if available."""
    global _embedder
    if _embedder is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading embedding model: {MODEL_NAME}")
            _embedder = SentenceTransformer(MODEL_NAME)
            logger.info("Embedding model loaded successfully.")
        except Exception as e:
            logger.info(f"Sentence-transformers not loaded ({e}) — using joint TF-IDF fallback.")
            _embedder = None
    return _embedder


def embed_pair(old_texts: List[str], new_texts: List[str]) -> Tuple[np.ndarray, np.ndarray]:
    """
    Embeds both old and new text lists in the EXACT same feature space.
    Guarantees X.shape[1] == Y.shape[1] for cosine similarity.
    """
    model = get_embedder()

    if model is not None:
        try:
            old_emb = model.encode(old_texts, batch_size=32, show_progress_bar=False, normalize_embeddings=True)
            new_emb = model.encode(new_texts, batch_size=32, show_progress_bar=False, normalize_embeddings=True)
            return np.array(old_emb), np.array(new_emb)
        except Exception as e:
            logger.warning(f"Neural embedder failed ({e}) — using joint TF-IDF.")

    # Joint TF-IDF fallback fitted on combined vocabulary
    combined = list(old_texts) + list(new_texts)
    if not combined or all(not t.strip() for t in combined):
        dim = 128
        return np.zeros((len(old_texts), dim)), np.zeros((len(new_texts), dim))

    vectorizer = TfidfVectorizer(max_features=512, stop_words="english", token_pattern=r"(?u)\b\w+\b")
    matrix = vectorizer.fit_transform(combined)
    norm_matrix = normalize(matrix.toarray(), norm="l2")

    n_old = len(old_texts)
    old_emb = norm_matrix[:n_old]
    new_emb = norm_matrix[n_old:]

    return old_emb, new_emb


def embed_chunks(texts: List[str]) -> np.ndarray:
    """Embeds a single list of texts."""
    model = get_embedder()
    if model is not None:
        try:
            emb = model.encode(texts, batch_size=32, show_progress_bar=False, normalize_embeddings=True)
            return np.array(emb)
        except Exception:
            pass

    if not texts or all(not t.strip() for t in texts):
        return np.zeros((len(texts), 128))

    vectorizer = TfidfVectorizer(max_features=512, stop_words="english", token_pattern=r"(?u)\b\w+\b")
    matrix = vectorizer.fit_transform(texts)
    return normalize(matrix.toarray(), norm="l2")
