import sys
from pathlib import Path
for _p in Path(__file__).resolve().parents:
    if (_p / 'backend').is_dir() and (_p / 'pyproject.toml').is_file():
        if str(_p) not in sys.path:
            sys.path.insert(0, str(_p))
        break

import math
import re
from typing import List, Dict, Any, Optional
from collections import Counter
import httpx
from backend.app.core.config import settings
from backend.app.core.logger import logger


class EmbeddingEngine:
    """Pluggable embedding engine supporting offline TF-IDF vectorization, Gemini, and OpenAI."""

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """Simple alphanumeric tokenizer with lowercasing."""
        return re.findall(r"\b[a-zA-Z0-9_\-]{2,}\b", text.lower())

    @classmethod
    def generate_vector(cls, text: str, vocabulary: Optional[List[str]] = None) -> List[float]:
        """Generates a dense/sparse normalized feature vector for text."""
        provider = settings.EMBEDDING_PROVIDER.lower()

        # If Gemini API key is configured and selected
        if provider == "gemini" and settings.GEMINI_API_KEY:
            try:
                return cls._embed_gemini(text)
            except Exception as e:
                logger.warning(f"Gemini embedding failed ({e}), falling back to tfidf_cosine")

        # If OpenAI API key is configured and selected
        if provider == "openai" and settings.OPENAI_API_KEY:
            try:
                return cls._embed_openai(text)
            except Exception as e:
                logger.warning(f"OpenAI embedding failed ({e}), falling back to tfidf_cosine")

        # Default: deterministic term-frequency normalized vector
        tokens = cls._tokenize(text)
        if not tokens:
            return [0.0] * 64

        counts = Counter(tokens)
        
        # If no vocabulary provided, hash tokens into fixed 128-dim feature vector
        dim = 128
        vec = [0.0] * dim
        for tok, cnt in counts.items():
            idx = abs(hash(tok)) % dim
            # TF weighting with sublinear scale
            vec[idx] += 1.0 + math.log(cnt)

        # L2 normalize
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]

        return vec

    @staticmethod
    def _embed_gemini(text: str) -> List[float]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={settings.GEMINI_API_KEY}"
        payload = {
            "model": "models/text-embedding-004",
            "content": {"parts": [{"text": text[:2000]}]}
        }
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["embedding"]["values"]

    @staticmethod
    def _embed_openai(text: str) -> List[float]:
        url = "https://api.openai.com/v1/embeddings"
        headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
        payload = {
            "model": "text-embedding-3-small",
            "input": text[:2000]
        }
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["data"][0]["embedding"]

    @staticmethod
    def cosine_similarity(v1: List[float], v2: List[float]) -> float:
        """Computes cosine similarity between two unit vectors."""
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        dot = sum(a * b for a, b in zip(v1, v2))
        return max(-1.0, min(1.0, dot))

