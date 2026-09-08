## Purpose

Defines pluggable connectors for Agentic RAG (PGVector), relational databases, Google Calendar, Google Sheets, and custom skills attached to Agno agents with scoped permissions.

## ADDED Requirements

### Requirement: Agentic RAG Connector via PGVector
The system SHALL provide vector-based knowledge retrieval tool adapters using PostgreSQL `pgvector` with tenant-isolated namespaces.

#### Scenario: RAG document search during conversation
- **WHEN** an agent encounters a business-specific question requiring knowledge base grounding
- **THEN** the Agno agent executes the RAG retrieval tool to query relevant text chunks from the tenant's PGVector namespace

### Requirement: Google Calendar & Sheets Connectors
The system SHALL expose Google Calendar availability/booking tools and Google Sheets read/write tools to Agno agents under OAuth permission scopes.

#### Scenario: Customer requests appointment booking
- **WHEN** a customer asks to schedule an appointment via WhatsApp
- **THEN** the agent invokes the Google Calendar tool to inspect open slots and create the event

### Requirement: Custom Skills Toolkit
The system SHALL support packaged Python skill tools that can be bound to agents via configuration.

#### Scenario: Custom skill tool invocation
- **WHEN** an agent spec binds a custom skill (e.g. `order_lookup`)
- **THEN** the Agno runtime exposes the skill function to the LLM tool-calling loop with input validation
