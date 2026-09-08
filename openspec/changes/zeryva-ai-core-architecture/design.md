## Context

Zeryva AI is a multi-tenant platform for running AI sales/customer support agents on WhatsApp. See `proposal.md` for background and capabilities.

This design document specifies the core technical architecture, data model, Pure Agno orchestration patterns, Meta WhatsApp Cloud API webhooks, and PostgreSQL storage details.

---

## Goals / Non-Goals

**Goals:**
- **Pure Agno Orchestration:** Use the `agno` framework cleanly for agent execution, tools, and multi-turn session management.
- **Dynamic Multi-Provider LLMs:** Allow individual agents/tenants to select different LLM providers (NVIDIA NIM, OpenAI, Anthropic, Ollama, etc.) dynamically.
- **PostgreSQL JSONB Prompt & Config Store:** Maintain system prompts, tool bindings, and versioned agent definitions in PostgreSQL using `JSONB`.
- **Meta WhatsApp Official Cloud API Integration:** Use Meta's official Cloud API for receiving webhook events and sending responses.
- **Dual Creation Engines:** Method 1 (Prompt Builder) and Method 2 (Structured Markdown spec parser) compiling into identical PostgreSQL `JSONB` schemas.

**Non-Goals:**
- Non-WhatsApp messaging channels (Instagram, Telegram, Web chat) in Phase 1.
- Enterprise SSO / SAML integration in Phase 1 (basic multi-tenant RBAC with JWT is in scope).
- Live voice calls.

---

## Decisions

### 1. Database Architecture: PostgreSQL with JSONB & PGVector

**Decision:** Store tenant metadata, agent configurations, version history, prompt templates, tool permissions, and conversation logs in PostgreSQL. Use `JSONB` columns for dynamic prompt and connector metadata, and `pgvector` extension for agentic RAG document embeddings.

#### Database Schema DDL Blueprint:

```sql
-- Tenants Table
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- WhatsApp Numbers / Accounts
CREATE TABLE whatsapp_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    phone_number_id VARCHAR(100) UNIQUE NOT NULL,
    waba_id VARCHAR(100) NOT NULL,
    access_token TEXT NOT NULL,
    verify_token VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agents Table
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    creation_method VARCHAR(50) NOT NULL, -- 'prompt_builder' or 'markdown_spec'
    current_version INT DEFAULT 1,
    status VARCHAR(50) DEFAULT 'active', -- 'draft', 'active', 'archived'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent Versions (Houses JSONB System Prompt, LLM Choice, Tool Config)
CREATE TABLE agent_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    version_number INT NOT NULL,
    system_prompt TEXT NOT NULL,
    llm_provider VARCHAR(50) NOT NULL, -- 'openai', 'nvidia_nim', 'anthropic'
    llm_model_name VARCHAR(100) NOT NULL,
    llm_params JSONB DEFAULT '{}'::jsonb, -- temperature, max_tokens
    connectors_config JSONB DEFAULT '[]'::jsonb, -- active connectors & permissions
    guardrails_config JSONB DEFAULT '{}'::jsonb, -- thresholds, escalation rules
    raw_source_spec TEXT, -- Original MD spec if Method 2
    created_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(agent_id, version_number)
);

-- Sessions & Conversation Memory
CREATE TABLE conversation_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    customer_phone_number VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'ai_active', -- 'ai_active', 'human_takeover', 'closed'
    history JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(tenant_id, customer_phone_number)
);

-- RAG Knowledge Base (PGVector)
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE knowledge_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    document_name VARCHAR(255),
    content TEXT NOT NULL,
    embedding vector(1536), -- Dimension based on model (e.g. OpenAI / NIM)
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

*Alternatives Considered:* 
- *MongoDB:* Lacks strong relational constraints for multi-tenant billing, version FKs, and PGVector co-location.
- *Separate DB per Tenant:* Too much infrastructure management overhead for early phase SMB scaling.

---

### 2. Pure Agno Orchestration & Dynamic LLM Factory

**Decision:** Wrap the Agno `Agent` instantiation in a dynamic factory service (`AgentFactory`). Based on `agent_versions.llm_provider`, instantiate the corresponding Agno Model adapter (`OpenAIChat`, `NvidiaNIM`, `Claude`, etc.) at runtime per request.

```python
# Conceptual Pure Agno Dynamic Factory Structure
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.nvidia import NvidiaNIM
from agno.models.anthropic import Claude

class AgnoAgentFactory:
    @staticmethod
    def create_agent(agent_version_data: dict, tools: list) -> Agent:
        provider = agent_version_data["llm_provider"]
        model_name = agent_version_data["llm_model_name"]
        system_prompt = agent_version_data["system_prompt"]
        params = agent_version_data.get("llm_params", {})

        if provider == "openai":
            model = OpenAIChat(id=model_name, **params)
        elif provider == "nvidia_nim":
            model = NvidiaNIM(id=model_name, **params)
        elif provider == "anthropic":
            model = Claude(id=model_name, **params)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

        return Agent(
            model=model,
            instructions=system_prompt,
            tools=tools,
            show_tool_calls=True,
            markdown=True
        )
```

---

### 3. Meta WhatsApp Official Cloud API Pipeline

**Decision:** Build a dedicated `WhatsAppService` using Meta's Cloud API:
1. **Webhook Ingest (`/api/v1/webhooks/whatsapp`):**
   - GET mode: Meta Webhook Verification (`hub.challenge`).
   - POST mode: Signature validation via HMAC-SHA256 using Meta App Secret.
   - Extracts sender `from` phone, `message_id`, and `text` or `media`.
2. **Orchestrator Processing:**
   - Checks `conversation_sessions.status`. If `human_takeover`, ignores auto-reply.
   - Runs Agno Agent with conversation history.
3. **Outbound Dispatcher:**
   - Calls Meta Graph API endpoint: `https://graph.facebook.com/v18.0/{phone_number_id}/messages`.

---

### 4. Method 1 & Method 2 Compiler Specifications

- **Method 1 Compiler (Prompt Builder):** Takes user form inputs (Business Name, Industry, Offerings, Tone, FAQs) $\rightarrow$ formats a standardized structured System Prompt $\rightarrow$ inserts into `agent_versions` with `version_number=1`.
- **Method 2 Parser (Markdown Spec):** Parses `.md` specs with defined section blocks:
  - `# Agent Specification: [Agent Name]`
  - `## Persona & Role`
  - `## Rules & Safety`
  - `## Tools & Connectors`
  - `## Escalation Rules`
  Translates these Markdown headers directly into system prompt instructions and connector JSONB configurations.

---

## Risks / Trade-offs

- **LLM Provider API Key Management** $\rightarrow$ *Mitigation:* Store customer API keys encrypted at rest using AES-256 (`Fernet` / KMS) in PostgreSQL.
- **Meta WhatsApp 24-Hour Session Window** $\rightarrow$ *Mitigation:* Support Meta Template Messages for initiating outbound messages outside the 24-hour customer window.
- **Tool Latency on WhatsApp** $\rightarrow$ *Mitigation:* Implement strict timeouts on external tool calls (Calendar/Sheets) and return graceful fallback responses if an API hangs beyond 5 seconds.

---

## Project Execution & Directory Structure

When ready to implement, the Zeryva AI project structure will be organized as:

```text
zeryva-ai/
├── app/
│   ├── main.py
│   ├── config/             # Environment & settings
│   ├── db/                 # PostgreSQL connection & SQLAlchemy/asyncpg models
│   ├── models/             # Pydantic schemas & DTOs
│   ├── services/
│   │   ├── whatsapp.py     # Meta Cloud API Webhook & Outbound SDK
│   │   ├── agent_engine.py # Pure Agno Agent Orchestrator & LLM Factory
│   │   ├── compiler.py     # Method 1 (Prompt) & Method 2 (MD Parser)
│   │   └── connectors/     # RAG, Calendar, Sheets, Skills adapters
│   └── api/                # FastAPI routers (webhooks, agent management)
├── tests/
└── docker-compose.yml
```
