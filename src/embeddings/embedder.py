import os
from typing import Sequence

from openai import OpenAI


DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"


class EmbeddingError(Exception):
    """Base exception for embedding-related errors."""


class MissingOpenAIAPIKeyError(EmbeddingError):
    """Raised when OPENAI_API_KEY is not set."""


def create_embedding(
        text: str,
        model: str = DEFAULT_EMBEDDING_MODEL
) -> list[float]:
    """
    Create a single embedding for the provided text.

    Args:
        text: Input text for embedding.
        model: Embedding model name.

    Returns:
        Embedding vector as a list of floats.

    Raises:
        MissingOpenAIAPIKeyError: If OPENAI_API_KEY is missing.
        EmbeddingError: If text is empty or API call fails.
    """
    cleaned_text = text.strip()

    if not cleaned_text:
        raise EmbeddingError("Cannot create embedding for empty text.")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise MissingOpenAIAPIKeyError("OPENAI_API_KEY is not set.")

    client = OpenAI(api_key=api_key)

    try:
        response = client.embeddings.create(
            model=model,
            input=cleaned_text,
        )
    except Exception as exc:
        raise EmbeddingError(f"Failed to create embedding: {exc}") from exc

    return response.data[0].embedding


def create_embeddings(
        texts: Sequence[str],
        model: str = DEFAULT_EMBEDDING_MODEL
) -> list[list[float]]:
    """
    Create embeddings for multiple texts in one request.

    Args:
        texts: Sequence of input texts.
        model: Embedding model name.

    Returns:
        List of embedding vectors.

    Raises:
        MissingOpenAIAPIKeyError: If OPENAI_API_KEY is missing.
        EmbeddingError: If input is empty or API call fails.
    """
    cleaned_texts = [text.strip() for text in texts]

    if not cleaned_texts:
        raise EmbeddingError("Input texts list is empty.")

    if any(not text for text in cleaned_texts):
        raise EmbeddingError("All texts must be non-empty.")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise MissingOpenAIAPIKeyError("OPENAI_API_KEY is not set.")

    client = OpenAI(api_key=api_key)

    try:
        response = client.embeddings.create(
            model=model,
            input=cleaned_texts,
        )
    except Exception as exc:
        raise EmbeddingError(f"Failed to create embeddings: {exc}") from exc

    return [item.embedding for item in response.data]
