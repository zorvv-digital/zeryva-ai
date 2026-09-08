## 1. Database & Project Foundation Setup

- [x] 1.1 Scaffold `zeryva-ai` project directory, dependencies (`agno`, `fastapi`, `uvicorn`, `asyncpg`, `sqlalchemy`, `pgvector`, `pydantic`), and verify environment initialization.
- [ ] 1.2 Implement PostgreSQL DDL migrations for `tenants`, `whatsapp_accounts`, `agents`, `agent_versions`, `conversation_sessions`, and `knowledge_embeddings` (with `pgvector`) tables, verifying migration execution against PostgreSQL.

## 2. Pure Agno Runtime Engine & LLM Provider Factory

- [ ] 2.1 Build `AgnoAgentFactory` service dynamically instantiating `OpenAIChat`, `NvidiaNIM`, or `Claude` model adapters based on agent configuration, verifying provider instantiation via unit tests.
- [ ] 2.2 Implement multi-turn session memory retrieval and persistence in PostgreSQL `conversation_sessions`, verifying context continuity across test turns.
- [ ] 2.3 Add confidence thresholds and human handoff guardrails, verifying thread status updates to `human_takeover`.

## 3. Meta WhatsApp Official Cloud API Integration

- [ ] 3.1 Implement FastAPI Webhook router for Meta WhatsApp verification (`hub.challenge`) and inbound message ingestion with HMAC-SHA256 signature validation, verifying payload parsing with mock webhooks.
- [ ] 3.2 Build Meta Graph API HTTP client for outbound text, media, and template message dispatching, verifying message sending against sandbox endpoint.

## 4. Agent Configuration Compilers (Method 1 & Method 2)

- [ ] 4.1 Implement Method 1 Prompt Builder intake compiler generating structured system prompt and JSONB agent version record in PostgreSQL.
- [ ] 4.2 Implement Method 2 Markdown Spec Parser parsing `.md` persona, policy, and tool binding sections into PostgreSQL `agent_versions` with version incrementing.

## 5. Connector Framework & RAG Pipeline

- [ ] 5.1 Implement PGVector Agentic RAG retrieval tool adapter for Agno agents, verifying query similarity search over embedded tenant documents.
- [ ] 5.2 Implement Google Calendar availability/booking and Google Sheets read/write tool adapters, verifying tool-calling loop execution within Agno agent.
