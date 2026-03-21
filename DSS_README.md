# Homeopathy AI DSS Vision

## Vision

This project should become a conversational decision support system, not just a chat bot.

The chat interface is the front door. The real value is behind it:
- convert free-text case narratives into structured symptoms
- map those symptoms to rubrics
- rank remedies from explicit evidence
- explain why each option appears
- show what is still missing or uncertain
- keep the final decision with the practitioner

The target user is a practitioner who wants a faster and more consistent path from narrative intake to reviewable remedy candidates.

## Product Goal

The core goal is traceable case handling:

1. A patient or practitioner enters the case in chat.
2. The system extracts structured findings.
3. The system stores those findings as session state.
4. The system maps findings to repertory rubrics.
5. The system scores candidate remedies.
6. The system retrieves supporting Materia Medica evidence.
7. The system explains the top candidates.
8. The practitioner reviews and decides.

That is what makes this a DSS rather than a generic chat experience.

## Architecture

### Interface Layer

Files:
- `main.py`
- `static/chat.html`
- `api/chat_routes.py`
- `api/session_routes.py`

Responsibilities:
- create and resume sessions
- accept chat messages
- return follow-up questions
- expose analysis output

### Session Orchestration Layer

File:
- `services/session_manager.py`

Responsibilities:
- create sessions
- store messages
- track symptom state
- track missing dimensions
- decide when analysis is ready

### Extraction Layer

Files:
- `services/symptom_extractor.py`
- `services/rubric_mapper.py`

Responsibilities:
- detect symptom phrases
- classify them by dimension
- attach rubric ids and rubric paths when possible
- provide deterministic extraction in local development

### Evidence and Ranking Layer

Files:
- `services/repertory_engine.py`
- `services/rag_service.py`
- `services/remedy_ranker.py`

Responsibilities:
- score remedies from rubrics
- retrieve Materia Medica support
- combine repertory, RAG, and outcomes into final ranking

### Explanation Layer

File:
- `llm/case_agent.py`

Responsibilities:
- generate follow-up phrasing
- explain remedy ranking
- show differentiators and missing context

## Interface Direction

The long-term interface should be practitioner-first.

### Left Panel: Chat Intake

Purpose:
- collect the case in plain language
- ask one targeted follow-up question at a time

Should show:
- session id
- conversation history
- current intake stage
- AI follow-up question

### Right Panel: DSS State

Purpose:
- make the reasoning visible instead of opaque

Should show:
- extracted symptoms grouped by dimension
- matched rubrics
- missing dimensions
- analysis readiness
- top remedies with scores
- evidence excerpts
- warnings for low confidence or insufficient data

## Data Flow

### Intake Flow

1. `POST /api/v1/chat/{session_id}/message`
2. store user message
3. extract structured symptoms
4. map symptoms to rubrics
5. persist session state
6. compute missing dimensions
7. decide next question or analysis readiness
8. return assistant reply plus structured extraction

### Analysis Flow

1. `POST /api/v1/chat/{session_id}/analyse`
2. load collected rubrics
3. score remedies with the repertory engine
4. retrieve Materia Medica passages
5. combine signals in the remedy ranker
6. generate explanation
7. return ranked remedies and evidence

## Sample Input

```text
I have a throbbing headache. It gets worse from light and noise. At night I feel afraid and restless.
```

## Sample Structured Output

```json
{
  "session_id": "e7f3b6a3-8f34-4dd7-9ac8-3b4dfde6a5d2",
  "stage": "symptom_collection",
  "symptoms_extracted": [
    {
      "text": "head pain",
      "dimension": "location",
      "normalized": "head pain",
      "rubric_path": null,
      "rubric_id": null,
      "confidence": 0.88
    },
    {
      "text": "throbbing headache",
      "dimension": "sensation",
      "normalized": "throbbing headache",
      "rubric_path": "Head > Pain > Throbbing",
      "rubric_id": 1001,
      "confidence": 0.95
    },
    {
      "text": "headache worse from light",
      "dimension": "modality_aggravation",
      "normalized": "worse from light",
      "rubric_path": "Head > Pain > Light aggravates",
      "rubric_id": 1002,
      "confidence": 0.95
    },
    {
      "text": "headache worse from noise",
      "dimension": "modality_aggravation",
      "normalized": "worse from noise",
      "rubric_path": "Head > Pain > Worse from noise",
      "rubric_id": 1004,
      "confidence": 0.95
    },
    {
      "text": "fear at night",
      "dimension": "mental",
      "normalized": "fear at night",
      "rubric_path": "Mind > Fear > Night",
      "rubric_id": 2001,
      "confidence": 0.92
    },
    {
      "text": "restlessness",
      "dimension": "general",
      "normalized": "restlessness",
      "rubric_path": "Generals > Restlessness",
      "rubric_id": 3001,
      "confidence": 0.9
    }
  ],
  "analysis_ready": true
}
```

## Sample Analysis Output

```json
{
  "session_id": "e7f3b6a3-8f34-4dd7-9ac8-3b4dfde6a5d2",
  "top_remedies": [
    {
      "remedy": "Belladonna",
      "repertory_score": 9.0,
      "rag_score": 0.92,
      "outcome_prior": 0.5,
      "final_score": 0.876,
      "matching_rubrics": [
        "Head > Pain > Throbbing",
        "Head > Pain > Light aggravates",
        "Head > Pain > Worse from noise"
      ]
    },
    {
      "remedy": "Arsenicum album",
      "repertory_score": 7.0,
      "rag_score": 0.0,
      "outcome_prior": 0.5,
      "final_score": 0.4889,
      "matching_rubrics": [
        "Mind > Fear > Night",
        "Generals > Restlessness"
      ]
    }
  ],
  "explanation": "Top remedy: Belladonna. It matches the dominant headache rubrics and is supported by Materia Medica excerpts describing throbbing headache with sensitivity to light and noise."
}
```

## What Makes It a DSS

This system becomes a real DSS when it does these things well:
- captures structured evidence from messy language
- shows exactly what evidence it used
- separates strong evidence from weak evidence
- explains why options rank where they do
- shows what information is still missing
- lets outcome feedback improve future ranking

Without those properties, it is only a chat wrapper.

## Near-Term Build Plan

### Phase 1

Make the current prototype coherent:
- deterministic symptom extraction fallback
- rubric mapping for known symptom patterns
- unique rubric persistence
- stable analysis readiness checks
- visible session state

### Phase 2

Strengthen reasoning:
- implement a real LLM client
- add ontology-backed rubric mapping
- improve question planning
- improve explanation generation

### Phase 3

Make it practitioner-ready:
- richer UI with visible state and evidence
- case review and outcome tracking
- confidence labels and warnings
- audit trail and export

## Interface Principles

- Ask one focused question at a time.
- Never hide the structured interpretation.
- Separate evidence from recommendation.
- Prefer traceability over fluent but opaque output.
- Keep the practitioner as the final decision-maker.
