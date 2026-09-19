# Agent Routes Specification

## Purpose

Defines unified API endpoint routing, tag organization, and documentation hierarchy for Agent Builder, Projects, Profiler, and System Health endpoints.

## Requirements

### Requirement: Consolidated Agent Builder Endpoint

The system SHALL expose the Agent Builder generation endpoint exclusively under the Agents namespace at `POST /api/v1/agents/builder/generate`. The system SHALL NOT expose a redundant top-level `/api/v1/builder/generate-agent` endpoint.

#### Scenario: Generate Agent via Agent Builder
- **WHEN** an HTTP POST request is received at `/api/v1/agents/builder/generate` with valid `BuilderInput`
- **THEN** the system returns a `200 OK` status with `BuilderAgentResponse` payload containing the synthesized agent configuration.

#### Scenario: Rejection of legacy endpoint
- **WHEN** an HTTP request is made to `/api/v1/builder/generate-agent`
- **THEN** the system SHALL return a `404 Not Found` response.

### Requirement: OpenAPI Tag Ordering and System Tagging

The system SHALL render OpenAPI documentation (`/api/v1/openapi.json` and `/docs`) with tags ordered logically as: Projects, Profiler, Agents, System. The `/api/v1/health` endpoint MUST be tagged with `System`.

#### Scenario: OpenAPI JSON Schema Inspection
- **WHEN** a client fetches `/api/v1/openapi.json`
- **THEN** the `paths` object contains definitions for Projects, Profiler, Agents, and `/api/v1/health` under the `System` tag, and no endpoint is assigned to the `default` tag group.
