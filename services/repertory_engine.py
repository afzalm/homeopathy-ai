"""
Repertory Engine Service
========================
Queries Neo4j graph to score remedies from matched rubrics.
Grade weights: 3→4pts, 2→2pts, 1→1pt
"""

import logging
from dataclasses import dataclass, field
from core.config import settings

logger = logging.getLogger(__name__)

GRADE_WEIGHTS = {3: 4, 2: 2, 1: 1}


@dataclass
class RemedyCandidate:
    name:             str
    repertory_score:  float = 0.0
    matching_rubrics: list[str] = field(default_factory=list)
    grade_breakdown:  dict = field(default_factory=dict)


class RepertoryEngine:

    def __init__(self):
        """
        In production, inject a Neo4j driver:

            from neo4j import AsyncGraphDatabase
            self.driver = AsyncGraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
        """
        self.driver = None   # replace with Neo4j driver

    async def score_remedies(
        self,
        rubric_paths: list[str]
    ) -> list[RemedyCandidate]:
        """
        For each rubric, query Neo4j for remedies and grades.
        Aggregate scores across all rubrics.
        Returns sorted list of RemedyCandidates.
        """
        if not rubric_paths:
            return []

        scores: dict[str, RemedyCandidate] = {}

        for rubric_path in rubric_paths:
            rubric_remedies = await self._query_rubric(rubric_path)

            for remedy_name, grade in rubric_remedies:
                if remedy_name not in scores:
                    scores[remedy_name] = RemedyCandidate(name=remedy_name)

                weight = GRADE_WEIGHTS.get(grade, 1)
                scores[remedy_name].repertory_score += weight
                scores[remedy_name].matching_rubrics.append(rubric_path)
                scores[remedy_name].grade_breakdown[rubric_path] = grade

        # Sort descending by score
        ranked = sorted(scores.values(), key=lambda x: x.repertory_score, reverse=True)
        return ranked[:settings.MAX_CANDIDATE_REMEDIES]

    async def _query_rubric(self, rubric_path: str) -> list[tuple[str, int]]:
        """
        Query Neo4j for remedies associated with a rubric.

        Cypher query:
            MATCH (r:Rubric {path: $path})-[i:INDICATES]->(rem:Remedy)
            RETURN rem.name AS remedy, i.grade AS grade
            ORDER BY i.grade DESC

        Returns list of (remedy_name, grade) tuples.

        Production implementation:
            async with self.driver.session() as session:
                result = await session.run(
                    "MATCH (r:Rubric {path: $path})-[i:INDICATES]->(rem:Remedy) "
                    "RETURN rem.name AS remedy, i.grade AS grade ORDER BY i.grade DESC",
                    path=rubric_path
                )
                return [(rec["remedy"], rec["grade"]) async for rec in result]
        """
        # ── Stub data for development ─────────────────────
        stub_data = {
            "Head > Pain > Throbbing": [
                ("Belladonna", 3), ("Glonoinum", 2), ("Natrum mur", 1),
                ("Melilotus", 2),  ("Sanguinaria", 2),
            ],
            "Head > Pain > Light aggravates": [
                ("Belladonna", 3), ("Sanguinaria", 2), ("Natrum mur", 2),
                ("Nux vomica", 1),
            ],
            "Head > Pain > Bursting": [
                ("Bryonia", 3), ("Glonoinum", 3), ("Belladonna", 2),
            ],
            "Head > Pain > Worse from noise": [
                ("Belladonna", 3), ("Nux vomica", 2), ("Coffea", 2),
            ],
            "Mind > Fear > Night": [
                ("Aconite", 3), ("Arsenicum album", 3), ("Stramonium", 2),
            ],
            "Generals > Restlessness": [
                ("Arsenicum album", 3), ("Aconite", 3), ("Rhus tox", 2),
            ],
        }
        return stub_data.get(rubric_path, [])
