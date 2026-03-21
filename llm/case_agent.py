"""
LLM Client & Case Agent
=======================
Wraps LLM API calls.
Handles: case-taking conversation, explanation generation.
"""

import asyncio
import json
import logging
from urllib import error, request

from core.config import settings

logger = logging.getLogger(__name__)

CASE_TAKING_SYSTEM = """
You are a homeopathic case-taking assistant helping a practitioner collect a complete symptom picture.

Rules:
- Ask ONE focused question at a time
- Never suggest or mention remedy names
- Never diagnose or interpret symptoms medically
- Be warm, clear, and professional
- Use plain language the patient can understand
"""

EXPLANATION_SYSTEM = """
You are a homeopathic clinical analysis assistant.
Base your explanation ONLY on the provided context.
Do not add any knowledge not present in the context.
Be concise, precise, and cite your sources.
"""

EXPLANATION_PROMPT = """
Generate a clinical case analysis for the top remedy candidates.

Patient symptoms:
{symptom_summary}

Repertory rubrics matched:
{rubric_list}

Remedy scores:
{remedy_scores}

Materia Medica excerpts:
{materia_medica}

For each of the top 3 remedies:
1. List matching rubrics
2. Cite the relevant Materia Medica text
3. Note any key differentiating features

Keep the explanation concise and clinically useful.
"""


class LLMClient:

    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.model = settings.LLM_MODEL

    async def complete(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Send a completion request to the configured LLM provider.

        Anthropic implementation:
            import anthropic
            client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            message = await client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text

        OpenAI implementation:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            response = await client.chat.completions.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        """
        if self.provider == "openrouter":
            return await self._openrouter_chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
            )

        raise NotImplementedError(
            f"Configure LLM provider '{self.provider}' in core/config.py "
            f"and implement LLMClient.complete()"
        )

    async def chat(
        self,
        system: str,
        messages: list[dict],
        max_tokens: int = 500
    ) -> str:
        """
        Multi-turn chat completion.

        messages format:
            [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]

        Anthropic implementation:
            import anthropic
            client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            response = await client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                messages=messages
            )
            return response.content[0].text
        """
        if self.provider == "openrouter":
            payload_messages = [{"role": "system", "content": system}] + messages
            return await self._openrouter_chat_completion(
                messages=payload_messages,
                max_tokens=max_tokens,
            )

        raise NotImplementedError("Implement LLMClient.chat()")

    async def _openrouter_chat_completion(
        self,
        messages: list[dict],
        max_tokens: int,
    ) -> str:
        api_key = settings.OPENROUTER_API_KEY.strip()
        if not api_key:
            raise NotImplementedError("Set OPENROUTER_API_KEY to use the openrouter provider")

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
        }

        response_data = await asyncio.to_thread(self._post_openrouter_request, payload, api_key)
        return self._extract_chat_content(response_data)

    def _post_openrouter_request(self, payload: dict, api_key: str) -> dict:
        base_url = settings.OPENROUTER_BASE_URL.rstrip("/")
        endpoint = f"{base_url}/chat/completions"
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            endpoint,
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": settings.OPENROUTER_HTTP_REFERER,
                "X-Title": settings.OPENROUTER_APP_TITLE,
            },
        )

        try:
            with request.urlopen(req, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            logger.error("OpenRouter HTTP error %s: %s", exc.code, detail)
            raise RuntimeError(f"OpenRouter request failed ({exc.code}): {detail}") from exc
        except error.URLError as exc:
            logger.error("OpenRouter connection error: %s", exc)
            raise RuntimeError(f"OpenRouter connection failed: {exc.reason}") from exc

    @staticmethod
    def _extract_chat_content(response_data: dict) -> str:
        choices = response_data.get("choices", [])
        if not choices:
            raise RuntimeError("OpenRouter response did not include any choices")

        message = choices[0].get("message", {})
        content = message.get("content")
        if isinstance(content, str) and content.strip():
            return content.strip()

        if isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text" and item.get("text"):
                    text_parts.append(item["text"])
            if text_parts:
                return "\n".join(text_parts).strip()

        raise RuntimeError("OpenRouter response did not contain message text")


class CaseAgent:
    """
    Manages LLM-driven conversational case-taking.
    Receives session state and generates the next response.
    """

    def __init__(self):
        self.llm = LLMClient()

    async def generate_response(
        self,
        conversation_history: list[dict],
        session_state: dict,
        next_question: str | None,
    ) -> str:
        """
        Generate the assistant's next conversational turn.

        If next_question is provided by the question planner,
        the LLM wraps it in natural language.
        If None, the LLM acknowledges that analysis is ready.
        """
        if next_question:
            # Give the LLM the planned question to phrase naturally
            instruction = (
                f"Acknowledge what the patient just said, then ask this question: "
                f"'{next_question}'"
            )
        else:
            instruction = (
                "The case information is now sufficient for analysis. "
                "Let the patient know you are now analysing their symptoms."
            )

        messages = conversation_history + [
            {"role": "user", "content": instruction}
        ]

        return await self.llm.chat(
            system=CASE_TAKING_SYSTEM,
            messages=messages,
        )

    async def generate_explanation(
        self,
        symptom_summary: str,
        rubric_list: list[str],
        remedy_scores: list[dict],
        materia_medica_excerpts: list[str],
    ) -> str:
        """Generate RAG-grounded remedy explanation."""
        prompt = EXPLANATION_PROMPT.format(
            symptom_summary=symptom_summary,
            rubric_list="\n".join(rubric_list),
            remedy_scores="\n".join(
                f"{r['remedy']}: {r['final_score']:.2f}" for r in remedy_scores
            ),
            materia_medica="\n\n".join(materia_medica_excerpts),
        )

        return await self.llm.complete(
            prompt=prompt,
            max_tokens=settings.LLM_MAX_TOKENS,
        )
