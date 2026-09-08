## Purpose

Provides a unified PostgreSQL JSONB schema and dual compilation pipeline for defining, versioning, and managing AI agent configurations across Method 1 (Prompt Builder) and Method 2 (Markdown Specs).

## ADDED Requirements

### Requirement: Unified Agent Configuration Schema in PostgreSQL
The system SHALL store agent system prompts, persona definitions, LLM selection, and connector bindings as JSONB documents inside PostgreSQL tables.

#### Scenario: Agent creation and retrieval
- **WHEN** an agent configuration is saved or loaded
- **THEN** PostgreSQL reads/writes the structured JSONB document containing system prompt, model choice, tool permissions, and escalation rules

### Requirement: Method 1 Prompt-Based Configuration Generator
The system SHALL accept natural language intake responses from business owners and compile them into a valid agent JSONB configuration.

#### Scenario: Guided intake compilation
- **WHEN** a business owner fills out the guided setup prompt form
- **THEN** the compiler transforms business details, tone, FAQs, and rules into an initial PostgreSQL agent configuration

### Requirement: Method 2 Markdown Spec Parser
The system SHALL parse structured Markdown definition files (defining persona, policies, tool bindings, and workflows) and compile them into valid agent JSONB documents with versioning.

#### Scenario: Markdown spec file upload
- **WHEN** an internal ops user submits an agent `.md` specification document
- **THEN** the parser validates syntax, extracts tool/connector definitions, compiles it to JSONB, increments the agent version number, and stores it in PostgreSQL
