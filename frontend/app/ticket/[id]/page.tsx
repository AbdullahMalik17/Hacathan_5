import { Metadata } from "next"
import { notFound } from "next/navigation"
import { TicketStatus } from "@/components/ticket-status"

interface Props {
  params: Promise<{ id: string }>
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

async function getTicket(id: string) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/ticket/${id}`, {
      cache: "no-store",
    })

    if (!res.ok) {
      return null
    }

    return res.json()
  } catch (error) {
    console.error("Failed to fetch ticket:", error)
    return null
  }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params

  return {
    title: `Ticket ${id.slice(0, 8)}...`,
    description: "Track the status of your support ticket",
  }
}

export default async function TicketPage({ params }: Props) {
  const { id } = await params
  const ticket = await getTicket(id)

  if (!ticket) {
    notFound()
  }

  return (
    <div className="min-h-[calc(100vh-4rem)] py-16">
      <div className="container">
        <div className="mx-auto max-w-3xl">
          <TicketStatus ticket={ticket} />
        </div>
      </div>
    </div>
  )
}
