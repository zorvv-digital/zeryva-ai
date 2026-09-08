# Business Requirements Document (BRD)
## WhatsApp AI Agent Platform

**Version:** 1.0
**Date:** September 9, 2026
**Status:** Draft

---

## 1. Executive Summary

This platform enables businesses to deploy AI-powered agents on WhatsApp that act as their sales or customer support teams. Businesses connect their own data and tools (databases, vector-based knowledge bases, Google Calendar, Sheets, and custom skills) so the agent behaves as a knowledgeable representative of that specific business. Agents can be created either through a guided, prompt-based builder (self-serve, business-owner-friendly) or through a structured configuration method using Markdown/text definitions plus connector wiring (used by an internal ops/implementation team for higher-touch or more complex client setups).

The platform targets SMBs first, with a path to mid-market/enterprise accounts, and monetizes via a hybrid model combining a base subscription with usage-based charges (e.g., conversations/messages, connector calls).

---

## 2. Business Objectives

- Enable non-technical business owners to launch a working WhatsApp AI agent within minutes using natural language/prompts.
- Enable an internal ops/solutions team to build more complex, tailored agents for clients using structured definitions (MD/text) and connector configuration.
- Reduce cost of customer support and increase sales conversion for SMBs by automating first-line WhatsApp conversations.
- Build a recurring revenue base (subscriptions) supplemented by usage-based revenue that scales with customer value/usage.
- Establish a defensible platform through a growing library of connectors and skills.

## 3. Background & Problem Statement

- SMBs increasingly receive customer inquiries via WhatsApp but lack staff/budget to staff always-on sales/support teams.
- Generic chatbots fail because they don't have access to the business's actual data (inventory, bookings, FAQs, policies) and can't take real actions (checking calendars, updating sheets, querying a database).
- Businesses want an agent that "knows" their business specifically, not a generic assistant — this requires an easy way to connect the agent to the business's actual systems and knowledge.
- Building custom AI agents in-house requires technical expertise most SMBs don't have; mid-market/enterprise clients may want more control and are often served better through an internal implementation team.

## 4. Target Market & Customer Segments

**Primary (Phase 1): SMBs**
- Local retail, clinics/healthcare practices, salons/spas, restaurants, real estate agents, small agencies, service providers (repair, consulting, coaching).
- Pain: high inquiry volume on WhatsApp, limited staff, need for 24/7 responsiveness.

**Secondary (Phase 2+): Mid-market / Enterprise**
- Larger businesses or multi-location brands needing more customization, governance, and integration depth.
- Likely onboarded with help from an internal ops/solutions team rather than pure self-serve.

**Internal users:**
- Ops/implementation team who build and maintain agents on behalf of clients using the MD/text + connector method, typically for higher-complexity or higher-value accounts.

## 5. Proposed Solution (Business View)

A web-based SaaS platform where a business:
1. Signs up and connects their WhatsApp Business number.
2. Creates an AI agent via one of two methods:
   - **Prompt-based builder:** Business owner describes their business, offerings, tone, and rules in natural language; the platform's agent builder generates a working agent configuration.
   - **Structured/MD method:** Internal ops team (or advanced users) define the agent using Markdown/text specification files, explicitly wiring connectors, tools, and skills — used for more complex or bespoke deployments.
3. Connects relevant tools/connectors: databases, vector DB for agentic RAG (knowledge base grounding), Google Calendar (bookings/scheduling), Google Sheets (data read/write), and other "skills" (reusable capabilities/integrations).
4. The agent then operates autonomously on WhatsApp: answering questions, qualifying/converting leads, booking appointments, escalating to humans when needed, and taking actions via connected tools.

## 6. Key Business Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| BR-1 | Support WhatsApp Business API integration for sending/receiving messages | Must |
| BR-2 | Provide a prompt-based, no-code agent builder for business owners | Must |
| BR-3 | Provide a structured MD/text-based agent definition method for internal ops team | Must |
| BR-4 | Support connector framework: DB tools, vector DB/RAG, Google Calendar, Google Sheets, extensible "skills" | Must |
| BR-5 | Support human handoff/escalation when the agent cannot resolve a query | Must |
| BR-6 | Provide analytics/reporting on conversations, conversions, and agent performance | Must |
| BR-7 | Support multi-tenant architecture (isolated data/config per business) | Must |
| BR-8 | Support hybrid billing: base subscription + usage-based metering | Must |
| BR-9 | Provide role-based access (business owner, ops/admin, agents) | Should |
| BR-10 | Support agent versioning/rollback for structured (MD) agents | Should |
| BR-11 | Provide a marketplace/library of prebuilt skills/connectors | Could |
| BR-12 | Support multi-language conversations | Could |
| BR-13 | Support additional channels beyond WhatsApp (Instagram, web chat) in future | Won't (this phase) |

## 7. Success Metrics (Business KPIs)

- Number of active businesses onboarded (Phase 1 target TBD)
- Monthly Recurring Revenue (MRR) from subscriptions
- Usage-based revenue as % of total revenue
- Average agent resolution rate (% of conversations resolved without human handoff)
- Customer retention / churn rate
- Time-to-first-working-agent (onboarding speed, especially for prompt-based builder)
- Net Promoter Score (NPS) among business owners

## 8. Constraints & Assumptions

- Dependent on WhatsApp Business API/Meta policies and approval processes.
- Assumes businesses are willing to connect sensitive data (DBs, calendars, sheets) to a third-party platform — requires strong security/compliance posture.
- Internal ops team is a real, staffed function in early phases (not purely self-serve for Method 2).
- Assumes usage-based pricing components are cost-transparent enough to avoid bill shock (relevant given LLM inference costs).

## 9. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| WhatsApp/Meta policy changes or API access restrictions | High | Abstract messaging layer; monitor policy changes; diversify channels long-term |
| Agent gives incorrect info / hallucinates in customer-facing context | High | RAG grounding, guardrails, confidence thresholds, human escalation |
| Data privacy/security concerns from connecting business systems | High | Strong encryption, scoped OAuth permissions, compliance certifications (SOC2, etc.) |
| Usage-based costs unpredictable for customers | Medium | Usage caps, alerts, transparent dashboards |
| Ops team becomes a bottleneck for Method 2 agents | Medium | Templatize MD specs, build internal tooling to speed up builds |
| Competition from generic chatbot/AI platforms | Medium | Differentiate via deep connector ecosystem + WhatsApp-native focus |

## 10. Stakeholders

- Founders/Product leadership
- Engineering (platform, integrations, AI/agent runtime)
- Internal Ops/Solutions team (Method 2 agent builders)
- Sales/Marketing (SMB acquisition)
- Customers: business owners, their end customers (WhatsApp users)

## 11. Out of Scope (Phase 1)

- Non-WhatsApp channels
- Full enterprise-grade custom SLAs
- White-labeling/reseller program (may be Phase 2+)
