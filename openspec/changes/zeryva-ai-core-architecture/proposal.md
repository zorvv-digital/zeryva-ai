## Why

Zeryva AI requires a multi-tenant platform architecture that enables businesses to deploy customizable AI sales/support agents on WhatsApp. Grounded in the business's own databases, knowledge bases (RAG), and tools (Google Calendar/Sheets/Skills), Zeryva AI supports both self-serve prompt-based setup for SMBs (Method 1) and structured Markdown/text specs for internal ops teams handling complex client builds (Method 2).

## What Changes

- Establish the core multi-tenant **Pure Agno** agent orchestration runtime with dynamic multi-provider LLM routing (OpenAI, NVIDIA NIM, Anthropic, etc. per tenant/agent).
- Implement direct integration with **Meta WhatsApp Official Cloud API** for inbound webhooks and outbound messaging (text, media, template compliance).
- Build the **PostgreSQL + JSONB** data and configuration storage schema for agent definitions, prompt templates, version control, and multi-tenant isolation.
- Define the dual creation specification engines:
  - **Method 1:** Prompt-based guided builder compiling natural language into PostgreSQL JSONB agent configs.
  - **Method 2:** Structured Markdown spec parser compiling `.md` files into PostgreSQL JSONB agent configs.
- Design the **Connector Framework** incorporating Agentic RAG (`pgvector`), DB tools, Google Calendar, Google Sheets, human handoff webhooks, and custom skills.

## Capabilities

### New Capabilities
- `zeryva-core/agent-runtime`: Multi-tenant pure Agno agent runtime with dynamic per-tenant LLM provider factory.
- `zeryva-core/whatsapp-channel`: Meta WhatsApp Official Cloud API integration for webhook ingestion and message delivery.
- `zeryva-core/agent-configuration`: Dual agent configuration engines (Method 1 prompt builder & Method 2 MD parser) backed by PostgreSQL JSONB schema.
- `zeryva-core/connector-framework`: Pluggable connector architecture for Agentic RAG (PGVector), DB tools, Google Calendar, Google Sheets, and human escalation.

### Modified Capabilities

None.

## Impact

- **New System Architecture:** Defines the foundational multi-tenant schema, agent runtime, connector framework, and API layers.
- **Dependencies:** Python 3.11+, FastAPI, Pure Agno framework (`agno`), PostgreSQL (`asyncpg`/`SQLAlchemy` + `pgvector`), Meta WhatsApp Cloud API SDK / HTTP Client.
- **Data Model:** PostgreSQL database housing multi-tenant configurations, JSONB prompt templates, version histories, and `pgvector` knowledge embeddings.
