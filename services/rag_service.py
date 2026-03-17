"""
RAG — Materia Medica Retrieval Service
=======================================
Retrieves relevant Materia Medica passages using pgvector similarity search.
Uses LangChain for orchestration.
"""

import logging
from dataclasses import dataclass
from core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class MateriaMedicaChunk:
    remedy:     str
    text:       str
    source:     str
    chapter:    str
    confidence: float


class MateriaMedicaRAG:

    def __init__(self):
        """
        Production setup:

            from langchain_community.vectorstores import PGVector
            from langchain_community.embeddings import HuggingFaceEmbeddings

            self.embeddings = HuggingFaceEmbeddings(
                model_name=settings.EMBEDDING_MODEL
            )
            self.vector_store = PGVector(
                connection_string=settings.DATABASE_URL,
                embedding_function=self.embeddings,
                collection_name="materia_vectors",
            )
        """
        self.vector_store = None   # replace with PGVector instance

    async def retrieve(
        self,
        remedy: str,
        symptoms: list[str],
        k: int = 4
    ) -> list[MateriaMedicaChunk]:
        """
        Retrieve Materia Medica passages for a remedy matching given symptoms.

        Production implementation:
            query = f"{remedy}: {', '.join(symptoms)}"
            docs  = self.vector_store.similarity_search_with_score(
                query,
                k=k,
                filter={"remedy_name": remedy}
            )
            return [
                MateriaMedicaChunk(
                    remedy=remedy,
                    text=doc.page_content,
                    source=doc.metadata.get("source", ""),
                    chapter=doc.metadata.get("chapter", ""),
                    confidence=float(score),
                )
                for doc, score in docs
            ]
        """
        # ── Stub data for development ─────────────────────
        stub_chunks = {
            "Belladonna": MateriaMedicaChunk(
                remedy="Belladonna",
                text=(
                    "Violent throbbing headaches with congestion. "
                    "Intense sensitivity to light, noise, and jarring. "
                    "Head hot, face red, pupils dilated. "
                    "Pain sudden in onset and sudden in cessation."
                ),
                source="Boericke Materia Medica",
                chapter="Head",
                confidence=0.92,
            ),
            "Glonoinum": MateriaMedicaChunk(
                remedy="Glonoinum",
                text=(
                    "Bursting, pulsating headache. "
                    "Head feels enormously large. "
                    "Surging of blood to head and heart. "
                    "Worse in the sun, worse from heat, worse from motion."
                ),
                source="Boericke Materia Medica",
                chapter="Head",
                confidence=0.87,
            ),
            "Natrum mur": MateriaMedicaChunk(
                remedy="Natrum mur",
                text=(
                    "Bursting headache as if a thousand little hammers. "
                    "Worse in morning on waking. "
                    "Associated with sun exposure and emotional suppression. "
                    "Headache better after sweating."
                ),
                source="Kent Materia Medica",
                chapter="Head",
                confidence=0.81,
            ),
        }
        chunk = stub_chunks.get(remedy)
        return [chunk] if chunk else []

    async def retrieve_top_remedies(
        self,
        remedies: list[str],
        symptoms: list[str],
    ) -> list[MateriaMedicaChunk]:
        """Retrieve Materia Medica for a list of candidate remedies."""
        all_chunks = []
        for remedy in remedies:
            chunks = await self.retrieve(remedy, symptoms)
            all_chunks.extend(chunks)
        return all_chunks
