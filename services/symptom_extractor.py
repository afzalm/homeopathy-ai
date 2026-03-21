"""
Symptom Extractor Service
=========================
Extracts structured symptom dimensions from patient text.
Uses LLM with structured JSON output when available and falls back to a
deterministic keyword extractor so the DSS pipeline still works in local
development.
"""

import json
import logging
from dataclasses import dataclass

from llm.case_agent import LLMClient
from models.schemas import SymptomExtracted
from services.rubric_mapper import RubricMapper

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """
You are a homeopathic symptom extraction engine.

Extract structured symptoms from the patient text below.
Return ONLY valid JSON. No explanation, no markdown.

Schema:
{{
  "symptoms": [
    {{
      "text": "original patient phrase",
      "dimension": "location|sensation|modality_aggravation|modality_amelioration|mental|general|time",
      "normalized": "normalized clinical term",
      "rubric_hint": "suggested Kent rubric path or null",
      "confidence": 0.0-1.0
    }}
  ]
}}

Rules:
- Extract every distinct symptom mentioned
- Modalities: anything that makes symptoms worse or better
- Mental symptoms: emotional/psychological states
- Generals: energy, sleep, appetite, thirst, temperature preference
- Confidence: 1.0 = clearly stated, 0.7 = inferred, 0.5 = ambiguous
- Return empty symptoms array if nothing clinical is mentioned

Patient text:
{patient_text}
"""


@dataclass(frozen=True)
class ExtractionRule:
    text: str
    dimension: str
    patterns: tuple[str, ...]
    normalized: str | None = None
    rubric_hint: str | None = None
    requires_context: tuple[str, ...] = ()
    confidence: float = 0.85


class SymptomExtractor:
    RULES: tuple[ExtractionRule, ...] = (
        ExtractionRule(
            text="head pain",
            dimension="location",
            normalized="head pain",
            patterns=("headache", "migraine", "pain in my head", "pain in the head", "head pain"),
            requires_context=("head", "headache", "migraine"),
            confidence=0.88,
        ),
        ExtractionRule(
            text="throbbing headache",
            dimension="sensation",
            normalized="throbbing headache",
            patterns=("throbbing", "pulsating", "pounding", "hammering"),
            rubric_hint="Head > Pain > Throbbing",
            requires_context=("head", "headache", "migraine"),
            confidence=0.95,
        ),
        ExtractionRule(
            text="bursting headache",
            dimension="sensation",
            normalized="bursting headache",
            patterns=("bursting", "splitting", "exploding"),
            rubric_hint="Head > Pain > Bursting",
            requires_context=("head", "headache", "migraine"),
            confidence=0.93,
        ),
        ExtractionRule(
            text="headache worse from light",
            dimension="modality_aggravation",
            normalized="worse from light",
            patterns=(
                "worse from light",
                "light makes it worse",
                "sensitive to light",
                "light aggravates",
                "photophobia",
            ),
            rubric_hint="Head > Pain > Light aggravates",
            requires_context=("head", "headache", "migraine"),
            confidence=0.95,
        ),
        ExtractionRule(
            text="headache worse from noise",
            dimension="modality_aggravation",
            normalized="worse from noise",
            patterns=(
                "worse from noise",
                "worse from light and noise",
                "noise makes it worse",
                "sensitive to noise",
                "noise aggravates",
                "light and noise",
            ),
            rubric_hint="Head > Pain > Worse from noise",
            requires_context=("head", "headache", "migraine"),
            confidence=0.95,
        ),
        ExtractionRule(
            text="fear at night",
            dimension="mental",
            normalized="fear at night",
            patterns=("fear at night", "afraid at night", "night fear", "fear during the night"),
            rubric_hint="Mind > Fear > Night",
            confidence=0.92,
        ),
        ExtractionRule(
            text="anxiety",
            dimension="mental",
            normalized="anxiety",
            patterns=("anxiety", "anxious", "nervous", "uneasy"),
            confidence=0.86,
        ),
        ExtractionRule(
            text="restlessness",
            dimension="general",
            normalized="restlessness",
            patterns=("restless", "restlessness", "cannot keep still", "can't keep still"),
            rubric_hint="Generals > Restlessness",
            confidence=0.9,
        ),
        ExtractionRule(
            text="low energy",
            dimension="general",
            normalized="low energy",
            patterns=("tired", "fatigue", "fatigued", "low energy", "exhausted"),
            confidence=0.86,
        ),
        ExtractionRule(
            text="poor sleep",
            dimension="general",
            normalized="poor sleep",
            patterns=("poor sleep", "cannot sleep", "can't sleep", "insomnia", "sleep is disturbed"),
            confidence=0.86,
        ),
        ExtractionRule(
            text="reduced appetite",
            dimension="general",
            normalized="reduced appetite",
            patterns=("loss of appetite", "reduced appetite", "poor appetite", "no appetite"),
            confidence=0.84,
        ),
    )

    def __init__(self):
        self.llm = LLMClient()
        self.rubric_mapper = RubricMapper()

    async def extract(self, patient_text: str) -> list[SymptomExtracted]:
        """
        Extract symptoms from patient text.
        Returns list of SymptomExtracted objects.
        """
        if not patient_text.strip():
            return []

        prompt = EXTRACTION_PROMPT.format(patient_text=patient_text)

        try:
            raw = await self.llm.complete(prompt, max_tokens=800)
            extracted = self._parse_response(raw)
            if extracted:
                return self._attach_rubrics(extracted)
        except NotImplementedError:
            logger.info("LLM extractor unavailable; using rule-based symptom extraction")
        except Exception as e:
            logger.error(f"Symptom extraction failed: {e}")

        return self._rule_based_extract(patient_text)

    def _parse_response(self, raw: str) -> list[SymptomExtracted]:
        try:
            cleaned = raw.strip().removeprefix("```json").removesuffix("```").strip()
            data = json.loads(cleaned)
            results = []

            for item in data.get("symptoms", []):
                text = item.get("text", "")
                dimension = item.get("dimension")
                normalized = item.get("normalized")
                rubric_hint = item.get("rubric_hint")
                rubric_id, rubric_path, rubric_confidence = self.rubric_mapper.map_symptom(
                    text=text,
                    dimension=dimension,
                    rubric_hint=rubric_hint,
                )
                results.append(SymptomExtracted(
                    text=text,
                    dimension=dimension,
                    normalized=normalized,
                    rubric_path=rubric_path or rubric_hint,
                    rubric_id=rubric_id,
                    confidence=max(float(item.get("confidence", 0.8)), rubric_confidence),
                ))

            return results

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Could not parse extraction response: {e}")
            return []

    def _rule_based_extract(self, patient_text: str) -> list[SymptomExtracted]:
        text_lower = patient_text.lower()
        results: list[SymptomExtracted] = []
        seen: set[tuple[str, str]] = set()

        for rule in self.RULES:
            if not any(pattern in text_lower for pattern in rule.patterns):
                continue
            if rule.requires_context and not any(term in text_lower for term in rule.requires_context):
                continue

            key = (rule.dimension, rule.text.lower())
            if key in seen:
                continue

            if rule.rubric_hint:
                rubric_id, rubric_path, rubric_confidence = self.rubric_mapper.map_symptom(
                    text=patient_text,
                    dimension=rule.dimension,
                    rubric_hint=rule.rubric_hint,
                    strict_hint=True,
                )
            else:
                rubric_id, rubric_path, rubric_confidence = (None, None, 0.0)
            results.append(SymptomExtracted(
                text=rule.text,
                dimension=rule.dimension,
                normalized=rule.normalized,
                rubric_path=rubric_path,
                rubric_id=rubric_id,
                confidence=max(rule.confidence, rubric_confidence),
            ))
            seen.add(key)

        return results

    def _attach_rubrics(self, extracted: list[SymptomExtracted]) -> list[SymptomExtracted]:
        enriched: list[SymptomExtracted] = []

        for symptom in extracted:
            rubric_id = symptom.rubric_id
            rubric_path = symptom.rubric_path
            rubric_confidence = 0.0

            if not rubric_id or not rubric_path:
                rubric_id, rubric_path, rubric_confidence = self.rubric_mapper.map_symptom(
                    text=symptom.text,
                    dimension=symptom.dimension,
                    rubric_hint=symptom.rubric_path,
                )

            enriched.append(SymptomExtracted(
                text=symptom.text,
                dimension=symptom.dimension,
                normalized=symptom.normalized,
                rubric_path=rubric_path,
                rubric_id=rubric_id,
                confidence=max(symptom.confidence, rubric_confidence),
            ))

        return enriched
