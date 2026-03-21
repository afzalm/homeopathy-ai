# Deployment

This repository can now be deployed as a single lightweight FastAPI container.

## Recommended Shape

Use this profile for a low-resource server:

- One application container
- SQLite persisted on a volume
- OpenRouter as the external LLM provider
- No PostgreSQL, Neo4j, or Redis for the first production pass

This matches the current codebase because the DSS flow, rubric mapping, and ranking all work with the local async SQLite path and stubbed repertory/RAG services.

## Coolify Setup

Create an application from the GitHub repository and use the root of this repo as the build context.

- Build pack: `Dockerfile`
- Dockerfile path: `Dockerfile`
- Port: `8000`
- Health check path: `/health`

## Persistent Storage

Add one persistent volume:

- Container path: `/app/data`

The app should use this database URL:

```env
DATABASE_URL=sqlite+aiosqlite:///./data/homeopathy_ai.db
```

## Required Environment Variables

Set these in Coolify:

```env
APP_NAME=Homeopathy AI
DEBUG=false
SECRET_KEY=replace-with-a-long-random-secret
ALLOWED_ORIGINS=["https://your-domain.com"]

DATABASE_URL=sqlite+aiosqlite:///./data/homeopathy_ai.db

LLM_PROVIDER=openrouter
LLM_MODEL=openai/gpt-4.1-mini
OPENROUTER_API_KEY=your-openrouter-api-key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_HTTP_REFERER=https://your-domain.com
OPENROUTER_APP_TITLE=Homeopathy AI DSS
```

## Optional Variables

These can stay at defaults unless you want to tune behavior:

```env
MIN_RUBRICS_FOR_ANALYSIS=4
MAX_CANDIDATE_REMEDIES=10
TOP_REMEDIES_RETURNED=5
WEIGHT_REPERTORY=0.50
WEIGHT_RAG=0.30
WEIGHT_OUTCOME=0.20
```

## Runtime Notes

- The root endpoint is `/`
- The practitioner UI is `/chat`
- Swagger docs are at `/docs`
- The health check is `/health`

## What This Deployment Does Not Yet Provision

This lightweight deployment does not set up:

- PostgreSQL
- Neo4j
- Redis
- vector embeddings infrastructure

Those services can be added later when you replace the current stub repertory and Materia Medica retrieval with live integrations.

## Recommended First Production Pass

1. Deploy this Docker image in Coolify.
2. Attach the `/app/data` persistent volume.
3. Set the OpenRouter environment variables.
4. Open `/chat` and verify session creation, symptom extraction, and analysis output.
5. Rotate any keys that were previously shared in plaintext.
