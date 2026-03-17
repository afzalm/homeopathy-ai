"""
Remedy Ranking Engine
=====================
Combines repertory scores + RAG similarity + outcome priors
into a final weighted ranking.
"""

import logging
from dataclasses import dataclass, field
from core.config import settings
from services.repertory_engine import RemedyCandidate
from services.rag_service import MateriaMedicaChunk

logger = logging.getLogger(__name__)


@dataclass
class RankedRemedy:
    remedy:           str
    repertory_score:  float
    rag_score:        float
    outcome_prior:    float
    final_score:      float
    matching_rubrics: list[str] = field(default_factory=list)


class RemedyRanker:

    def __init__(self):
        self.w_repertory = settings.WEIGHT_REPERTORY   # 0.50
        self.w_rag       = settings.WEIGHT_RAG         # 0.30
        self.w_outcome   = settings.WEIGHT_OUTCOME     # 0.20

    def rank(
        self,
        repertory_candidates: list[RemedyCandidate],
        rag_chunks:           list[MateriaMedicaChunk],
        outcome_priors:       dict[str, float] | None = None,
    ) -> list[RankedRemedy]:
        """
        Combine all signals into final ranked list.

        outcome_priors: dict of remedy_name → historical success rate (0–1)
        If not provided, defaults to 0.5 for all remedies (no prior).
        """
        if not repertory_candidates:
            return []

        outcome_priors = outcome_priors or {}

        # Normalise repertory scores to 0–1
        max_rep = max((c.repertory_score for c in repertory_candidates), default=1)
        rep_norm = {
            c.name: c.repertory_score / max_rep
            for c in repertory_candidates
        }

        # Build RAG similarity scores (0–1 from confidence)
        rag_scores: dict[str, float] = {}
        for chunk in rag_chunks:
            if chunk.remedy not in rag_scores:
                rag_scores[chunk.remedy] = chunk.confidence
            else:
                rag_scores[chunk.remedy] = max(rag_scores[chunk.remedy], chunk.confidence)

        ranked = []
        for candidate in repertory_candidates:
            rep   = rep_norm.get(candidate.name, 0)
            rag   = rag_scores.get(candidate.name, 0)
            prior = outcome_priors.get(candidate.name, 0.5)

            final = (
                self.w_repertory * rep +
                self.w_rag       * rag +
                self.w_outcome   * prior
            )

            ranked.append(RankedRemedy(
                remedy=candidate.name,
                repertory_score=round(candidate.repertory_score, 2),
                rag_score=round(rag, 3),
                outcome_prior=round(prior, 3),
                final_score=round(final, 4),
                matching_rubrics=candidate.matching_rubrics,
            ))

        ranked.sort(key=lambda x: x.final_score, reverse=True)
        return ranked[:settings.TOP_REMEDIES_RETURNED]
