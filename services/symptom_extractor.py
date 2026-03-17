"""
Symptom Extractor Service
=========================
Extracts structured symptom dimensions from patient text.
Uses LLM with structured JSON output.
In production: replace with fine-tuned model for this task.
"""

import json
import logging
from models.schemas import SymptomExtracted
from llm.case_agent import LLMClient

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """
You are a homeopathic symptom extraction engine.

Extract structured symptoms from the patient text below.
Return ONLY valid JSON. No explanation, no markdown.

Schema:
{
  "symptoms": [
    {
      "text": "original patient phrase",
      "dimension": "location|sensation|modality_aggravation|modality_amelioration|mental|general|time",
      "normalized": "normalized clinical term",
      "rubric_hint": "suggested Kent rubric path or null",
      "confidence": 0.0-1.0
    }
  ]
}

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


class SymptomExtractor:

    def __init__(self):
        self.llm = LLMClient()

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
            return self._parse_response(raw)
        except Exception as e:
            logger.error(f"Symptom extraction failed: {e}")
            return []

    def _parse_response(self, raw: str) -> list[SymptomExtracted]:
        try:
            cleaned = raw.strip().removeprefix("```json").removesuffix("```").strip()
            data    = json.loads(cleaned)
            results = []

            for item in data.get("symptoms", []):
                results.append(SymptomExtracted(
                    text=item.get("text", ""),
                    rubric_path=item.get("rubric_hint"),
                    rubric_id=None,   # resolved by ontology mapper
                    confidence=float(item.get("confidence", 0.8)),
                ))

            return results

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Could not parse extraction response: {e}")
            return []
