# Discovery Log: Customer Success FTE

**Date:** February 1, 2026
**Phase:** Incubation (Exercise 1.1)

## 1. Analysis of Sample Tickets
We analyzed 10 sample tickets across three channels (Email, WhatsApp, Web Form).

### Channel Patterns
| Channel | Characteristics | Example Tone |
| :--- | :--- | :--- |
| **Email** | Formal, structured (Subject/Body), detailed. | "Hi support... Can you send it to me? Thanks." |
| **WhatsApp** | Informal, concise, often lower-case, urgent. | "hey, how do i change my password?", "URGENT!" |
| **Web Form** | Semi-formal, categorical, specific. | "We are hitting 429 errors...", "Refund Request" |

### Query Categories
1.  **Knowledge Base (Automatable):**
    *   "How do I change my password?"
    *   "Can I add a guest user?"
    *   "Integration with Jira?"
2.  **Account/Transactional (Automatable with Context):**
    *   "Invoice missing" (Needs lookup, but likely standard procedure).
    *   "API Rate Limits" (Needs plan knowledge).
3.  **Escalation (Human Intervention):**
    *   **Legal:** "Data residency" (High risk).
    *   **Refunds:** "Please refund" (Financial policy).
    *   **Outages:** "Site is down" (Critical infra issue).

## 2. Agent Requirements Discovered
Based on the analysis, the agent must:

1.  **Channel Awareness:**
    *   Detect the source channel.
    *   Adjust response length (short for WhatsApp, detailed for Email).
    *   Adjust tone (casual vs. professional).

2.  **Intent Recognition:**
    *   Distinguish between "How-to" (KB Search) vs. "Action" (Refund/Legal).
    *   Identify "URGENT" keywords for prioritization.

3.  **Sentiment Analysis:**
    *   Detect frustration (e.g., "URGENT!", "Fix it NOW!").
    *   Pre-emptively escalate negative sentiment interactions.

4.  **Escalation Logic:**
    *   **Hard Rules:** Legal, Refunds, Outages -> Escalate.
    *   **Soft Rules:** Sentiment < 0.3 -> Escalate.

## 3. Next Steps (Prototype Plan)
*   Build a core loop that accepts `(content, channel, metadata)`.
*   Implement a `normalize_message` function.
*   Implement a `decide_action` function (Search KB vs. Escalate).
*   Implement `format_response` based on channel.
