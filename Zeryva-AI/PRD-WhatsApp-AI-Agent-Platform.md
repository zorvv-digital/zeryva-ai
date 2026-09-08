# Product Requirements Document (PRD)
## WhatsApp AI Agent Platform

**Version:** 1.0
**Date:** September 9, 2026
**Status:** Draft

---

## 1. Overview

A SaaS platform that lets businesses deploy an AI agent on WhatsApp to act as their sales/support team. The agent is grounded in the business's own data and tools via connectors (DB, vector DB/RAG, Google Calendar, Google Sheets, skills). Two creation paths exist: a **prompt-based agent builder** (self-serve, business-owner-facing) and a **structured MD/text + connector configuration** path (internal ops team, for complex/custom builds).

## 2. Goals

- Let a business owner go from signup to a working WhatsApp agent in under 15 minutes using the prompt-based builder.
- Let the internal ops team build precise, complex agents using structured MD/text specs with fine-grained connector/tool control.
- Ensure every agent response can be grounded in real business data (RAG) and can take real actions (via connectors) rather than just chatting.
- Provide clear observability (conversation logs, analytics) and safe failure modes (human handoff).

## 3. Non-Goals (v1)

- Channels other than WhatsApp.
- Fully automated, ops-team-free complex agent builds (Method 2 is explicitly ops-assisted in v1).
- Voice/call support.

## 4. User Personas

| Persona | Description | Primary Method |
|---|---|---|
| **Business Owner / SMB Admin** | Owns or manages the business; wants an agent live fast without technical work | Method 1: Prompt-based builder |
| **Internal Ops/Solutions Engineer** | Anthropic-internal (platform-internal) team member who builds/configures agents on behalf of clients | Method 2: MD/text + connectors |
| **End Customer (WhatsApp user)** | The business's customer messaging on WhatsApp | Interacts with the deployed agent |
| **Platform Admin** | Manages tenants, billing, connector marketplace, monitoring | Admin console |

## 5. Core User Flows

### 5.1 Business Owner Onboarding (Method 1 — Prompt Builder)
1. Sign up / create account.
2. Connect WhatsApp Business number (via Meta Business API flow).
3. Enter business details via guided prompts: business type, offerings/catalog, tone/persona, FAQs, escalation rules.
4. System (agent builder) generates an initial agent configuration (system prompt, initial knowledge base, suggested connectors).
5. Owner reviews/tests agent in a sandbox chat preview.
6. Owner connects relevant data sources (upload docs for RAG, connect calendar/sheets/DB as needed) via guided connector setup.
7. Owner publishes agent; it goes live on the connected WhatsApp number.
8. Owner monitors conversations/analytics; can edit agent via the same prompt-based interface.

### 5.2 Ops Team Build (Method 2 — MD/Text + Connectors)
1. Ops user creates a new agent workspace for a client.
2. Ops user writes/uploads an MD file (or text input) defining: persona, rules, workflows, tool-use policies, escalation logic.
3. Ops user attaches connectors/tools explicitly (DB schema mapping, vector DB namespace, Calendar, Sheets, custom skills) with scoped permissions.
4. Ops user tests agent in sandbox against sample conversations.
5. Ops user versions and publishes the agent to the client's WhatsApp number.
6. Ops user can iterate via updated MD versions (with rollback support).

### 5.3 End Customer Conversation Flow
1. Customer messages the business's WhatsApp number.
2. Agent retrieves relevant context (RAG over connected knowledge base + conversation history).
3. Agent decides: answer directly, call a tool/connector (e.g., check calendar availability, query DB for order status, update a sheet), or escalate to a human.
4. Agent responds; conversation and any tool calls are logged.
5. If confidence is low or the customer requests a human, agent hands off (notifies business owner/team, e.g., via dashboard or a notification channel).

## 6. Functional Requirements

### 6.1 Agent Creation — Method 1: Prompt-Based Builder
- FR-1.1: Guided intake form/chat that collects business info (type, products/services, tone, policies, FAQs).
- FR-1.2: Auto-generate an initial system prompt/config from intake responses.
- FR-1.3: Allow iterative refinement via natural-language edits ("make it more casual", "add a return policy rule").
- FR-1.4: Auto-suggest relevant connectors based on business type (e.g., a clinic → Calendar; a retailer → DB/Sheets for inventory).
- FR-1.5: Sandbox/test chat interface before publishing.

### 6.2 Agent Creation — Method 2: MD/Text + Connectors
- FR-2.1: Support agent definition via Markdown file upload or in-platform text editor.
- FR-2.2: Spec format supports: persona/role, rules/policies, workflows, tool/connector bindings, escalation conditions.
- FR-2.3: Explicit connector wiring UI — map a connector instance (e.g., specific Google Sheet, DB table, vector DB namespace) to the agent with scoped permissions (read/write).
- FR-2.4: Versioning of agent specs with diff view and rollback.
- FR-2.5: Sandbox testing with sample conversation transcripts / test cases.
- FR-2.6: Multi-agent workspace support for ops team managing multiple clients.

### 6.3 Connector & Tool Framework
- FR-3.1: Database connector — connect to common DBs (Postgres/MySQL/etc.) with read (and optionally scoped write) query capability exposed as tools to the agent.
- FR-3.2: Vector DB / Agentic RAG — ingest documents (PDF, docs, URLs, FAQs) into a vector store; agent retrieves relevant chunks at runtime; support per-business isolated namespaces.
- FR-3.3: Google Calendar connector — check availability, create/update/cancel events (for bookings/appointments).
- FR-3.4: Google Sheets connector — read/write rows (e.g., logging leads, checking inventory).
- FR-3.5: "Skills" framework — a plugin-like system for reusable, packaged capabilities (e.g., "order lookup," "lead qualification") that can be attached to any agent.
- FR-3.6: Connector permission scoping (least-privilege access per agent/business).
- FR-3.7: Connector marketplace/catalog (browsable list of available connectors/skills) — future phase.

### 6.4 WhatsApp Integration
- FR-4.1: Connect/verify a business's WhatsApp Business Account (via Meta's Cloud API or BSP).
- FR-4.2: Support text, media (images/docs), and template messages (for outbound/notification compliance).
- FR-4.3: Support session-based and 24-hour-window messaging rules per WhatsApp policy.
- FR-4.4: Multi-number support for businesses with multiple WhatsApp lines (e.g., multi-location).

### 6.5 Agent Runtime & Orchestration
- FR-5.1: Agent runtime executes: retrieve context (RAG) → reason → decide tool calls → respond.
- FR-5.2: Support multi-turn conversation memory per customer/session.
- FR-5.3: Guardrails: configurable topics/actions the agent must avoid or must escalate.
- FR-5.4: Human handoff mechanism: pause AI responses, notify a human, allow human to take over the thread.
- FR-5.5: Fallback behavior when a connector/tool call fails (graceful degradation, retry, or escalate).

### 6.6 Analytics & Monitoring
- FR-6.1: Conversation log viewer (searchable, filterable by outcome/date/agent).
- FR-6.2: Dashboard metrics: conversation volume, resolution rate, escalation rate, response time, (optionally) conversion/booking counts.
- FR-6.3: Usage metering dashboard (for billing transparency): messages processed, tool calls made, tokens/cost estimate.
- FR-6.4: Alerting for anomalies (e.g., spike in escalations, connector failures).

### 6.7 Billing & Plans
- FR-7.1: Base subscription tiers (e.g., by number of agents, connectors, or seats).
- FR-7.2: Usage-based metering and billing (e.g., per conversation or per message beyond plan allowance, per tool call).
- FR-7.3: Usage caps/alerts to prevent bill shock; ability to set spend limits.
- FR-7.4: Billing dashboard/invoicing, upgrade/downgrade flows.

### 6.8 Admin & Access Control
- FR-8.1: Role-based access: Business Owner, Business Team Member, Internal Ops, Platform Admin.
- FR-8.2: Multi-tenant data isolation (per business).
- FR-8.3: Audit log of agent config changes and connector permission changes.

## 7. Non-Functional Requirements

- **Security:** Encryption at rest/in transit; OAuth-based scoped connector access; SOC2-track compliance roadmap; PII handling controls.
- **Reliability:** High availability for message handling (target uptime TBD, e.g., 99.9%); graceful degradation if an LLM provider or connector is down.
- **Scalability:** Multi-tenant architecture must scale horizontally as agent/message volume grows.
- **Latency:** Agent response time target (e.g., <5–8s for typical WhatsApp reply) to feel responsive within WhatsApp UX norms.
- **Compliance:** Adherence to WhatsApp Business Policy and Meta commerce/messaging policies; data residency considerations if serving multiple regions.
- **Auditability:** All tool calls and data access by agents should be logged for traceability.

## 8. System Architecture (High-Level, Product View)

- **WhatsApp Messaging Layer** — integration with WhatsApp Cloud API/BSP.
- **Agent Builder Service** — prompt-based builder (Method 1) + MD/spec parser (Method 2).
- **Agent Runtime/Orchestrator** — handles reasoning, RAG retrieval, tool invocation, memory.
- **Connector Layer** — pluggable adapters for DB, Vector DB, Calendar, Sheets, Skills, each with scoped auth.
- **Vector DB / Knowledge Store** — per-tenant isolated namespaces for RAG.
- **Analytics/Logging Service** — conversation and tool-call logging, dashboards.
- **Billing/Metering Service** — usage tracking tied to subscription + usage-based billing.
- **Admin Console** — tenant management, RBAC, connector marketplace management.

*(Detailed technical architecture to be defined by engineering; this is the product-level view.)*

## 9. Phased Roadmap (Proposed)

**Phase 1 (MVP):**
- WhatsApp integration (single number per business)
- Method 1 prompt-based builder (core flow)
- Vector DB/RAG connector + Google Calendar + Google Sheets connectors
- Basic analytics dashboard
- Human handoff
- Base subscription billing only (usage-based can follow shortly after)

**Phase 2:**
- Method 2 MD/text builder + connector wiring for ops team
- DB connector, skills framework
- Usage-based billing component
- Versioning/rollback for agents

**Phase 3:**
- Connector/skills marketplace
- Multi-number/multi-location support
- Advanced RBAC, audit logs
- Additional language support

## 10. Open Questions

- What specific WhatsApp provider will be used (Meta Cloud API directly vs. a BSP like Twilio/360dialog/Gupshup)?
- What LLM provider(s)/models power the agent runtime, and how is cost passed through in usage billing?
- What are the specific connector priorities beyond the four named (DB, vector DB, Calendar, Sheets) for Phase 1 "skills"?
- What does "skills" concretely mean technically — prompt templates, function-calling tools, or packaged workflows?
- What are target pricing tiers/numbers for the base subscription and usage rates?
- Compliance requirements by target geography (data residency, WhatsApp Business Policy nuances per region)?

## 11. Appendix: Glossary

- **Agent:** An AI-driven persona configured to represent a specific business on WhatsApp.
- **Connector:** An integration adapter giving an agent access to an external system/tool (DB, Calendar, Sheets, etc.).
- **Agentic RAG:** Retrieval-Augmented Generation where the agent actively decides when/what to retrieve from a vector database as part of its reasoning.
- **Skill:** A packaged, reusable capability that can be attached to an agent (e.g., "book appointment," "check order status").
- **MD/Text Agent Spec:** A structured Markdown or text-based definition of an agent's persona, rules, and connector bindings, used in Method 2.
