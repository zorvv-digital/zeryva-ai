## Purpose

Provides a multi-tenant pure Agno agent execution engine that dynamically routes LLM requests to different providers (OpenAI, NVIDIA NIM, Anthropic) based on per-agent configuration.

## ADDED Requirements

### Requirement: Dynamic Multi-Provider LLM Factory
The agent runtime SHALL instantiate Agno agents with dynamically selected LLM provider models (OpenAI, NVIDIA NIM, Anthropic, or local LLMs) configured per tenant and agent profile.

#### Scenario: Agent configured with NVIDIA NIM
- **WHEN** an inbound message is assigned to an agent configured with NVIDIA NIM provider settings
- **THEN** the runtime instantiates the Agno Agent using the NVIDIA NIM model adapter with configured credentials

#### Scenario: Agent configured with OpenAI
- **WHEN** an inbound message is assigned to an agent configured with OpenAI provider settings
- **THEN** the runtime instantiates the Agno Agent using the OpenAI model adapter with tenant API keys

### Requirement: Multi-Turn Session Memory
The agent runtime SHALL maintain isolated multi-turn conversation memory per WhatsApp user session in PostgreSQL.

#### Scenario: Sequential user interaction
- **WHEN** an end customer sends follow-up messages within an active session
- **THEN** the agent runtime loads previous conversation history from PostgreSQL into the Agno agent context

### Requirement: Execution Guardrails and Safety Thresholds
The agent runtime SHALL enforce configurable guardrail policies and low-confidence fallbacks.

#### Scenario: Unsafe or out-of-scope query
- **WHEN** the agent output violates topic boundaries or confidence falls below threshold
- **THEN** the runtime triggers human handoff or returns a graceful safety response
