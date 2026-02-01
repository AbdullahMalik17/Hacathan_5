# Transition Checklist: General → Custom Agent

## 1. Discovered Requirements
- [x] **Channel Awareness:** Must distinguish Email (Formal) vs WhatsApp (Casual).
- [x] **Sentiment Monitoring:** Must track frustration to trigger early escalation.
- [x] **Context Persistence:** "How do I create one?" requires knowing the previous topic ("Boards").
- [x] **Keywords:** "Legal", "Refund", "Urgent" are reliable escalation triggers.

## 2. Working Prompts (Prototype Logic)
*   **Escalation:** `if "refund" in content or sentiment < 0.3 -> escalate`
*   **Search:** `if query is short and context exists -> query = query + context`
*   **Formatting:** `if channel == "whatsapp" -> strip newlines, add emojis, truncate`

## 3. Edge Cases Found
| Edge Case | How It Was Handled | Test Case Needed |
|-----------|-------------------|------------------|
| Empty message | (Not yet handled, assumed valid input) | Yes |
| Angry customer | Escalated via Sentiment Score | Yes |
| Legal threat | Escalated via Keyword | Yes |
| Vagueness | Ask for clarification (Basic default response) | Yes |

## 4. Response Patterns
- **Email:** "Dear Customer... [Detailed Body] ... Best regards, TechCorp Support"
- **WhatsApp:** "[Answer] 📱" (No greetings/signatures, very short)
- **Web:** "Hello... [Answer]"

## 5. Escalation Rules (Finalized)
- Trigger 1: Keywords ("lawyer", "refund", "outage")
- Trigger 2: Sentiment Score < 0.3
- Trigger 3: Explicit request ("speak to human")

## 6. Performance Baseline
- Average response time: < 0.1s (Local prototype)
- Accuracy on test set: High for keywords, Medium for semantic search (needs Vector DB).
- Escalation rate: 30% in test set (3/10 tickets escalated).
