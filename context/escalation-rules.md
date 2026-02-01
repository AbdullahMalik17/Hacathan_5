# Escalation Rules

## General Philosophy
Our AI agent handles routine inquiries. Any request requiring subjective judgment, financial authorization, legal interpretation, or dealing with highly emotional customers must be escalated to a human FTE.

## Trigger Conditions

### 1. Keyword Triggers
Escalate immediately if the customer mentions:
-   "Lawyer", "Attorney", "Sue", "Legal action"
-   "GDPR", "Compliance", "Data breach"
-   "Refund", "Chargeback", "Cancel subscription" (if retention logic fails)
-   "Speak to a human", "Real person", "Manager"

### 2. Sentiment Triggers
-   **Negative Sentiment:** If sentiment score < 0.3 (on a 0-1 scale) for two consecutive messages.
-   **Aggression:** Profanity, insults, or threats (e.g., "This is garbage", "I will destroy you").

### 3. Complexity Triggers
-   **Unknown Intent:** If the AI cannot determine the intent with >70% confidence after 2 attempts.
-   **Looping:** If the customer asks the same question twice after receiving an answer (indicates the answer wasn't helpful).
-   **Technical Depth:** Questions involving custom API implementation, specific code debugging, or server log analysis that are not covered in the standard docs.

### 4. Business Rules
-   **Enterprise Inquiries:** High-value leads asking for "Enterprise pricing" or "Custom contracts" should be routed to Sales.
-   **System Outages:** Reports of "System down", "500 error", or "Crash" should be flagged to Engineering (if not already known).

## Escalation Protocol
1.  **Acknowledge:** Tell the customer you are connecting them with a specialist.
    *   *Example:* "I understand this is important. I'm going to escalate this ticket to our Senior Support Team who can assist you further."
2.  **Tag:** Add the tag `needs_human` to the ticket.
3.  **Context:** Append a summary of the conversation and the reason for escalation to the internal notes.
4.  **Route:**
    *   `billing` -> Billing Team
    *   `technical` -> Tier 2 Support
    *   `sales` -> Sales Team
    *   `legal` -> Legal/Compliance
