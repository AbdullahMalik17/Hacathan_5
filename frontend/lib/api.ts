/**
 * API client for Customer Success Digital FTE
 * Task T060: API client for support form submission
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || ""

export interface SupportRequestData {
  name: string
  email: string
  subject: string
  message: string
  priority?: "normal" | "high"
}

export interface SupportRequestResponse {
  ticket_id: string
  status: string
  message?: string
}

export interface TicketStatusResponse {
  ticket_id: string
  status: "open" | "in_progress" | "resolved" | "escalated"
  category: string
  priority: "low" | "medium" | "high"
  source_channel: string
  created_at: string
  resolved_at?: string
  messages: Array<{
    id: string
    role: "customer" | "agent" | "system"
    content: string
    created_at: string
    channel: string
  }>
}

export interface ChatMessage {
  role: "user" | "assistant"
  content: string
}

export interface ChatResponse {
  response: string
  ticket_id?: string
}

/**
 * Submit a support request via web form.
 */
export async function submitSupportRequest(
  data: SupportRequestData
): Promise<SupportRequestResponse> {
  const response = await fetch(`${API_BASE_URL}/api/support/submit`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    const errorData = await response.json()
    throw new Error(errorData.detail || "Failed to submit support request")
  }

  return response.json()
}

/**
 * Get ticket status by ticket ID (FR-036).
 */
export async function getTicketStatus(
  ticketId: string
): Promise<TicketStatusResponse> {
  const response = await fetch(`${API_BASE_URL}/api/ticket/${ticketId}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
    cache: "no-store",
  })

  if (!response.ok) {
    const errorData = await response.json()
    throw new Error(errorData.detail || "Failed to fetch ticket status")
  }

  return response.json()
}

/**
 * Send a chat message to the AI agent.
 */
export async function sendChatMessage(
  message: string,
  conversationHistory: ChatMessage[] = []
): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message,
      conversation_history: conversationHistory,
    }),
  })

  if (!response.ok) {
    const errorData = await response.json()
    throw new Error(errorData.detail || "Failed to send chat message")
  }

  return response.json()
}

/**
 * Health check for API.
 */
export async function checkApiHealth(): Promise<{
  status: string
  service: string
}> {
  const response = await fetch(`${API_BASE_URL}/health`)

  if (!response.ok) {
    throw new Error("API health check failed")
  }

  return response.json()
}
