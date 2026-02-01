/**
 * Task T060: API client for support form submission
 * Requirements: FR-035 (web form submission)
 */

export interface SupportRequestData {
  name: string;
  email: string;
  subject: string;
  message: string;
  priority?: 'normal' | 'high';
}

export interface SupportRequestResponse {
  ticket_id: string;
  status: string;
  message?: string;
}

export interface TicketStatusResponse {
  ticket_id: string;
  status: string;
  category: string;
  priority: string;
  created_at: string;
  messages: Array<{
    role: string;
    content: string;
    created_at: string;
  }>;
}

/**
 * Submit a support request via web form.
 *
 * @param data Support request data
 * @returns Promise with ticket ID and status
 */
export async function submitSupportRequest(
  data: SupportRequestData
): Promise<SupportRequestResponse> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const response = await fetch(`${apiUrl}/api/support/submit`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to submit support request');
  }

  return response.json();
}

/**
 * Get ticket status by ticket ID (FR-036).
 *
 * @param ticketId Ticket UUID
 * @returns Promise with ticket details
 */
export async function getTicketStatus(ticketId: string): Promise<TicketStatusResponse> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const response = await fetch(`${apiUrl}/api/ticket/${ticketId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to fetch ticket status');
  }

  return response.json();
}

/**
 * Health check for API.
 *
 * @returns Promise with health status
 */
export async function checkApiHealth(): Promise<{ status: string; service: string }> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const response = await fetch(`${apiUrl}/health`);

  if (!response.ok) {
    throw new Error('API health check failed');
  }

  return response.json();
}
