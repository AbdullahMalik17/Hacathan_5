"use client"

import { useState } from "react"
import { toast } from "sonner"
import {
  Copy,
  Clock,
  CheckCircle2,
  AlertCircle,
  ArrowUpCircle,
  MessageSquare,
  User,
  Bot,
  RefreshCw,
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { cn } from "@/lib/utils"

interface Message {
  id: string
  role: "customer" | "agent" | "system"
  content: string
  created_at: string
  channel: string
}

interface Ticket {
  ticket_id: string
  status: "open" | "in_progress" | "resolved" | "escalated"
  category: string
  priority: "low" | "medium" | "high"
  created_at: string
  resolved_at?: string
  source_channel: string
  messages: Message[]
}

interface TicketStatusProps {
  ticket: Ticket
}

const statusConfig = {
  open: {
    label: "Open",
    variant: "info" as const,
    icon: Clock,
    description: "Your request is in the queue",
  },
  in_progress: {
    label: "In Progress",
    variant: "warning" as const,
    icon: RefreshCw,
    description: "Our AI agent is working on your request",
  },
  resolved: {
    label: "Resolved",
    variant: "success" as const,
    icon: CheckCircle2,
    description: "Your request has been resolved",
  },
  escalated: {
    label: "Escalated",
    variant: "destructive" as const,
    icon: ArrowUpCircle,
    description: "Transferred to human support team",
  },
}

const priorityConfig = {
  low: { label: "Low", variant: "secondary" as const },
  medium: { label: "Medium", variant: "outline" as const },
  high: { label: "High", variant: "warning" as const },
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  })
}

function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000)

  if (diffInSeconds < 60) return "Just now"
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`
  return `${Math.floor(diffInSeconds / 86400)}d ago`
}

export function TicketStatus({ ticket }: TicketStatusProps) {
  const [isRefreshing, setIsRefreshing] = useState(false)

  const status = statusConfig[ticket.status]
  const StatusIcon = status.icon

  const copyTicketId = () => {
    navigator.clipboard.writeText(ticket.ticket_id)
    toast.success("Ticket ID copied to clipboard")
  }

  const refreshStatus = async () => {
    setIsRefreshing(true)
    // Simulate refresh - in production, this would refetch
    await new Promise((resolve) => setTimeout(resolve, 1000))
    setIsRefreshing(false)
    toast.info("Ticket status refreshed")
    // In production: router.refresh() or revalidate
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header Card */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardDescription>Ticket ID</CardDescription>
              <div className="mt-1 flex items-center gap-2">
                <code className="font-mono text-lg font-semibold">
                  {ticket.ticket_id.slice(0, 8)}...
                </code>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={copyTicketId}
                  className="h-8 w-8"
                  aria-label="Copy full ticket ID"
                >
                  <Copy className="h-4 w-4" />
                </Button>
              </div>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={refreshStatus}
              disabled={isRefreshing}
            >
              <RefreshCw
                className={cn("mr-2 h-4 w-4", isRefreshing && "animate-spin")}
              />
              Refresh
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {/* Status Banner */}
          <div
            className={cn(
              "rounded-lg p-4",
              ticket.status === "resolved"
                ? "bg-emerald-50"
                : ticket.status === "escalated"
                  ? "bg-red-50"
                  : ticket.status === "in_progress"
                    ? "bg-amber-50"
                    : "bg-blue-50"
            )}
          >
            <div className="flex items-center gap-3">
              <div
                className={cn(
                  "flex h-10 w-10 items-center justify-center rounded-full",
                  ticket.status === "resolved"
                    ? "bg-emerald-100"
                    : ticket.status === "escalated"
                      ? "bg-red-100"
                      : ticket.status === "in_progress"
                        ? "bg-amber-100"
                        : "bg-blue-100"
                )}
              >
                <StatusIcon
                  className={cn(
                    "h-5 w-5",
                    ticket.status === "resolved"
                      ? "text-emerald-600"
                      : ticket.status === "escalated"
                        ? "text-red-600"
                        : ticket.status === "in_progress"
                          ? "text-amber-600"
                          : "text-blue-600"
                  )}
                />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <Badge variant={status.variant}>{status.label}</Badge>
                  <Badge variant={priorityConfig[ticket.priority].variant}>
                    {priorityConfig[ticket.priority].label} Priority
                  </Badge>
                </div>
                <p
                  className={cn(
                    "mt-1 text-sm",
                    ticket.status === "resolved"
                      ? "text-emerald-700"
                      : ticket.status === "escalated"
                        ? "text-red-700"
                        : ticket.status === "in_progress"
                          ? "text-amber-700"
                          : "text-blue-700"
                  )}
                >
                  {status.description}
                </p>
              </div>
            </div>
          </div>

          {/* Ticket Details */}
          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            <div>
              <p className="text-sm text-muted-foreground">Created</p>
              <p className="font-medium">{formatDate(ticket.created_at)}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Category</p>
              <p className="font-medium capitalize">{ticket.category}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Channel</p>
              <p className="font-medium capitalize">{ticket.source_channel}</p>
            </div>
            {ticket.resolved_at && (
              <div>
                <p className="text-sm text-muted-foreground">Resolved</p>
                <p className="font-medium">{formatDate(ticket.resolved_at)}</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Conversation History */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5" />
            Conversation History
          </CardTitle>
          <CardDescription>
            {ticket.messages?.length || 0} messages in this conversation
          </CardDescription>
        </CardHeader>
        <CardContent>
          {ticket.messages && ticket.messages.length > 0 ? (
            <div className="space-y-4">
              {ticket.messages.map((message, index) => (
                <div
                  key={message.id || index}
                  className={cn(
                    "flex gap-3",
                    message.role === "customer" ? "flex-row" : "flex-row-reverse"
                  )}
                >
                  <div
                    className={cn(
                      "flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
                      message.role === "customer"
                        ? "bg-primary"
                        : message.role === "agent"
                          ? "bg-accent"
                          : "bg-muted"
                    )}
                  >
                    {message.role === "customer" ? (
                      <User className="h-4 w-4 text-primary-foreground" />
                    ) : message.role === "agent" ? (
                      <Bot className="h-4 w-4 text-primary" />
                    ) : (
                      <AlertCircle className="h-4 w-4 text-muted-foreground" />
                    )}
                  </div>
                  <div
                    className={cn(
                      "max-w-[80%] rounded-lg px-4 py-2",
                      message.role === "customer"
                        ? "bg-primary text-primary-foreground"
                        : message.role === "agent"
                          ? "bg-muted"
                          : "bg-yellow-50 border border-yellow-200"
                    )}
                  >
                    <p className="text-sm">{message.content}</p>
                    <p
                      className={cn(
                        "mt-1 text-xs",
                        message.role === "customer"
                          ? "text-primary-foreground/70"
                          : "text-muted-foreground"
                      )}
                    >
                      {formatRelativeTime(message.created_at)}
                      {message.channel && ` • via ${message.channel}`}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-8 text-center">
              <MessageSquare className="mx-auto h-12 w-12 text-muted-foreground/50" />
              <p className="mt-2 text-muted-foreground">
                No messages yet. Our agent will respond shortly.
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Help Section */}
      <Card className="border-dashed">
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-muted-foreground" />
            <div>
              <p className="font-medium">Need more help?</p>
              <p className="mt-1 text-sm text-muted-foreground">
                If your issue hasn't been resolved or you need to add more
                information, you can reply to the email response or submit a new
                request referencing this ticket ID.
              </p>
              <div className="mt-3 flex gap-2">
                <Button variant="outline" size="sm" asChild>
                  <a href="/support">Submit New Request</a>
                </Button>
                <Button variant="outline" size="sm" asChild>
                  <a href="mailto:support@company.com">Email Support</a>
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
