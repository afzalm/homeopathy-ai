"""
Rubric mapping helpers.

Maps extracted symptom phrases onto the small rubric set currently supported by
the development stub repertory engine. This gives the chat flow a deterministic
path into rubric-based analysis before the full ontology and LLM mapping layer
is implemented.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class RubricRule:
    rubric_id: int
    rubric_path: str
    dimension: str
    patterns: tuple[str, ...]
    requires_context: tuple[str, ...] = ()
    confidence: float = 0.9


class RubricMapper:
    """Keyword-based rubric mapper for the current development rubric set."""

    RULES: tuple[RubricRule, ...] = (
        RubricRule(
            rubric_id=1001,
            rubric_path="Head > Pain > Throbbing",
            dimension="sensation",
            patterns=("throbbing", "pulsating", "pounding", "hammering"),
            requires_context=("head", "headache", "migraine"),
            confidence=0.95,
        ),
        RubricRule(
            rubric_id=1002,
            rubric_path="Head > Pain > Light aggravates",
            dimension="modality_aggravation",
            patterns=(
                "worse from light",
                "light makes it worse",
                "sensitive to light",
                "light aggravates",
                "photophobia",
            ),
            requires_context=("head", "headache", "migraine"),
            confidence=0.95,
        ),
        RubricRule(
            rubric_id=1003,
            rubric_path="Head > Pain > Bursting",
            dimension="sensation",
            patterns=("bursting", "splitting", "exploding"),
            requires_context=("head", "headache", "migraine"),
            confidence=0.93,
        ),
        RubricRule(
            rubric_id=1004,
            rubric_path="Head > Pain > Worse from noise",
            dimension="modality_aggravation",
            patterns=(
                "worse from noise",
                "worse from light and noise",
                "noise makes it worse",
                "sensitive to noise",
                "noise aggravates",
                "light and noise",
            ),
            requires_context=("head", "headache", "migraine"),
            confidence=0.95,
        ),
        RubricRule(
            rubric_id=2001,
            rubric_path="Mind > Fear > Night",
            dimension="mental",
            patterns=("fear at night", "afraid at night", "night fear", "fear during the night"),
            confidence=0.92,
        ),
        RubricRule(
            rubric_id=3001,
            rubric_path="Generals > Restlessness",
            dimension="general",
            patterns=("restless", "restlessness", "cannot keep still", "can't keep still"),
            confidence=0.9,
        ),
    )

    def map_symptom(
        self,
        text: str,
        dimension: str | None = None,
        rubric_hint: str | None = None,
        strict_hint: bool = False,
    ) -> tuple[int | None, str | None, float]:
        """Return a rubric match for the symptom text if one is known."""
        text_lower = text.lower()
        normalized_dimension = (dimension or "").lower()
        hinted_rule: RubricRule | None = None

        if rubric_hint:
            for rule in self.RULES:
                if rubric_hint.strip().lower() == rule.rubric_path.lower():
                    hinted_rule = rule
                    break

        best_rule: RubricRule | None = None
        best_score = 0

        if hinted_rule:
            hinted_score = self._score_rule_match(hinted_rule, text_lower, normalized_dimension)
            if strict_hint:
                if hinted_score > 0:
                    return hinted_rule.rubric_id, hinted_rule.rubric_path, hinted_rule.confidence
                return None, None, 0.0
            if hinted_score > 0:
                best_rule = hinted_rule
                best_score = hinted_score + 1

        for rule in self.RULES:
            score = self._score_rule_match(rule, text_lower, normalized_dimension)
            if not score:
                continue

            if score > best_score:
                best_rule = rule
                best_score = score

        if not best_rule:
            return None, None, 0.0

        return best_rule.rubric_id, best_rule.rubric_path, best_rule.confidence

    @staticmethod
    def _score_rule_match(
        rule: RubricRule,
        text_lower: str,
        normalized_dimension: str,
    ) -> int:
        pattern_hits = sum(1 for pattern in rule.patterns if pattern in text_lower)
        if not pattern_hits:
            return 0
        if rule.requires_context and not any(term in text_lower for term in rule.requires_context):
            return 0

        score = pattern_hits
        if normalized_dimension and normalized_dimension == rule.dimension:
            score += 1
        return score
