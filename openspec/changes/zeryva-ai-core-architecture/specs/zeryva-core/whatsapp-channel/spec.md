## Purpose

Integrates Meta's official WhatsApp Cloud API to receive inbound customer messages via webhooks and deliver agent responses asynchronously.

## ADDED Requirements

### Requirement: Meta Cloud API Webhook Ingestion
The system SHALL ingest inbound text, media, and interactive button responses from Meta's WhatsApp Cloud API webhook endpoint with signature verification.

#### Scenario: Inbound text message verification
- **WHEN** Meta sends a POST webhook payload containing an inbound WhatsApp message
- **THEN** the system verifies the SHA256 HMAC signature, extracts the sender phone number and message text, and queues it for the target tenant's agent engine

### Requirement: Outbound Messaging via Graph API
The system SHALL send agent text responses, media attachments, and structured message templates using Meta's WhatsApp Graph API.

#### Scenario: Agent sends text reply
- **WHEN** the Agno agent runtime produces a text response for an end customer
- **THEN** the system posts the message to Meta Graph API `/v18.0/{phone_number_id}/messages` and logs delivery status

### Requirement: Human Handoff Control Flow
The system SHALL pause AI responses for a phone number when human handoff is activated.

#### Scenario: Human agent takes over thread
- **WHEN** human handoff is triggered by agent or user request
- **THEN** the system flags the session state as `human_takeover` in PostgreSQL and stops auto-generating AI replies until released
