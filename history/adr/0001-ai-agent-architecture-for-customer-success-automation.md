# ADR-0001: AI Agent Architecture for Customer Success Automation

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-01-31
- **Feature:** 001-customer-success-fte
- **Context:** Building an autonomous AI employee to handle customer support inquiries 24/7 across three communication channels. The agent must operate reliably, follow strict workflows, and provide grounded responses without hallucination. Constitution Principle V (Agent Autonomy with Guardrails) requires explicit behavioral constraints and tool-based execution.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Core system behavior
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - LangChain, custom loops, other SDKs
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects all agent interactions
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

We will use **OpenAI Agents SDK** with the following integrated approach:

- **Agent Framework**: OpenAI Agents SDK with explicit workflow instructions
- **Tool Definitions**: @function_tool decorators for all agent capabilities
- **Schema Validation**: Pydantic v2 models for automatic type checking and schema generation
- **Workflow Enforcement**: Required tool execution order in agent instructions (create_ticket → get_customer_history → search_knowledge_base → send_response)
- **Guardrails**: Hard-coded escalation triggers for pricing, refund, legal keywords detected in tool functions
- **Response Grounding**: All responses must cite knowledge base search results (no hallucination)

**Implementation Pattern**:
```python
from openai_agents import Agent, function_tool
from pydantic import BaseModel

class TicketCreate(BaseModel):
    customer_id: str
    issue: str
    channel: str

@function_tool
def create_ticket(data: TicketCreate) -> str:
    """Create support ticket with automatic validation."""
    # Implementation with Pydantic validation
    pass

agent = Agent(
    name="customer-success-fte",
    instructions="REQUIRED WORKFLOW: 1. create_ticket 2. get_customer_history 3. search_knowledge_base 4. send_response",
    tools=[create_ticket, get_customer_history, search_knowledge_base, send_response, escalate_ticket],
)
```

## Consequences

### Positive

- **Type Safety**: Pydantic v2 models provide automatic schema generation and runtime validation, reducing errors from malformed tool inputs
- **Structured Outputs**: SDK eliminates manual JSON parsing and guarantees tool call format compliance
- **Workflow Control**: Explicit instruction ordering prevents agent from skipping critical steps (e.g., ticket creation before response)
- **Reliability**: Built-in retry logic and error handling reduce custom code maintenance
- **Observability**: SDK provides structured logging and tracing for debugging agent behavior
- **Constitution Alignment**: Directly supports Principle V (Agent Autonomy with Guardrails) through tool-based constraints

### Negative

- **Vendor Lock-in**: Tight coupling to OpenAI's SDK means switching to another provider (Anthropic, Cohere) requires significant refactoring
- **Black Box Behavior**: Limited visibility into SDK's internal decision-making process compared to custom agent loop
- **Version Risk**: SDK is relatively new; breaking changes in future versions could require code updates
- **Cost**: OpenAI API costs $0.60 per 1M tokens (vs open-source alternatives), estimated $600/year for 500k tokens/month
- **Latency**: Network round-trip to OpenAI API adds 200-500ms vs local models

## Alternatives Considered

### Alternative A: LangChain Agent Framework
- **Stack**: LangChain LCEL + Tool calling + Custom chains
- **Why Rejected**:
  - Less structured output guarantees compared to OpenAI SDK
  - More boilerplate code for validation and error handling
  - Constitution requires strict workflow enforcement which is harder to implement in LangChain's flexible chain model
  - Looser typing means more runtime errors

### Alternative B: Custom Agent Loop
- **Stack**: Custom ReAct loop + Manual tool calling + Anthropic Claude API
- **Why Rejected**:
  - Reinventing validation, retry logic, and workflow management
  - Higher maintenance burden for core agent infrastructure
  - Slower development velocity vs using battle-tested SDK
  - Team lacks deep expertise in agent loop design patterns
  - Would need to build equivalent of @function_tool decorators and Pydantic integration

### Alternative C: Open-Source Local Models (Llama 3, Mixtral)
- **Stack**: vLLM inference + Custom tool calling + Local hosting
- **Why Rejected**:
  - Lower accuracy for complex customer support queries (benchmarks show 15-20% worse on RAG tasks)
  - Requires GPU infrastructure ($200-400/month) negating cost savings
  - Deployment complexity (model serving, versioning, monitoring)
  - Slower iteration velocity during development

## References

- Feature Spec: specs/001-customer-success-fte/spec.md (FR-020: Agent Response Generation)
- Implementation Plan: specs/001-customer-success-fte/plan.md (Phase 0: Research - Section 1)
- Research Document: specs/001-customer-success-fte/research.md (Section 1: OpenAI Agents SDK Architecture)
- Related ADRs: ADR-0003 (Event-Driven Architecture) for agent worker integration with Kafka
- Constitution: .specify/memory/constitution.md (Principle V: Agent Autonomy with Guardrails)
