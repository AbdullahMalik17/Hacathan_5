# Agent Skills Manifest

## 1. Knowledge Retrieval Skill
*   **Description:** Capability to search and extract relevant information from the product knowledge base.
*   **Trigger:** User asks a question about product features, how-to guides, or troubleshooting.
*   **Tools:** `search_knowledge_base`
*   **Inputs:** `query` (string)
*   **Outputs:** Relevant documentation snippets.

## 2. Sentiment Analysis Skill
*   **Description:** Real-time monitoring of customer emotion to detect frustration or aggression.
*   **Trigger:** Every incoming message.
*   **Logic:**
    *   Score > 0.7: Positive (Record "Happy")
    *   Score < 0.3: Negative (Record "Frustrated")
    *   Score < 0.1: Aggressive (Trigger Escalation)
*   **Inputs:** `message_content`
*   **Outputs:** `sentiment_score` (float), `confidence` (float).

## 3. Escalation Decision Skill
*   **Description:** Governance logic to decide when a human must intervene.
*   **Trigger:** Post-response generation or pre-processing.
*   **Rules:**
    *   Keyword match: "Legal", "Sue", "Refund".
    *   Sentiment threshold: < 0.3.
    *   Complexity: 2 failed search attempts.
*   **Tools:** `escalate_to_human`

## 4. Channel Adaptation Skill
*   **Description:** Formatting logic to ensure responses fit the medium.
*   **Trigger:** Pre-send.
*   **Rules:**
    *   **Email:** Add formal greeting ("Dear X"), signature, standard formatting. Max 500 words.
    *   **WhatsApp:** Concise, emojis allowed, < 300 chars preferred. No signatures.
    *   **Web Form:** Semi-formal, direct answer.
*   **Tools:** `send_response` (internal formatting logic).

## 5. Customer Identification Skill
*   **Description:** Resolution of customer identity across channels.
*   **Trigger:** Incoming message.
*   **Logic:**
    *   Match `email` -> `customer_id`
    *   Match `phone` -> `customer_id`
    *   If no match -> Create new `customer_id`.
*   **Tools:** `get_customer_history`
