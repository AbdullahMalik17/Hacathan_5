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
  ArrowRight,
  Sparkles,
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Separator } from "@/components/ui/separator"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { cn } from "@/lib/utils"
import { motion } from "framer-motion"

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
    color: "blue",
    progress: 25,
  },
  in_progress: {
    label: "In Progress",
    variant: "warning" as const,
    icon: RefreshCw,
    description: "Our AI agent is working on your request",
    color: "amber",
    progress: 60,
  },
  resolved: {
    label: "Resolved",
    variant: "success" as const,
    icon: CheckCircle2,
    description: "Your request has been resolved",
    color: "emerald",
    progress: 100,
  },
  escalated: {
    label: "Escalated",
    variant: "destructive" as const,
    icon: ArrowUpCircle,
    description: "Transferred to human support team",
    color: "red",
    progress: 50,
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

const colorClasses = {
  blue: {
    bg: "bg-blue-50 dark:bg-blue-950/30",
    icon: "bg-blue-100 dark:bg-blue-900/50",
    iconText: "text-blue-600 dark:text-blue-400",
    text: "text-blue-700 dark:text-blue-300",
    border: "border-blue-200 dark:border-blue-800",
  },
  amber: {
    bg: "bg-amber-50 dark:bg-amber-950/30",
    icon: "bg-amber-100 dark:bg-amber-900/50",
    iconText: "text-amber-600 dark:text-amber-400",
    text: "text-amber-700 dark:text-amber-300",
    border: "border-amber-200 dark:border-amber-800",
  },
  emerald: {
    bg: "bg-emerald-50 dark:bg-emerald-950/30",
    icon: "bg-emerald-100 dark:bg-emerald-900/50",
    iconText: "text-emerald-600 dark:text-emerald-400",
    text: "text-emerald-700 dark:text-emerald-300",
    border: "border-emerald-200 dark:border-emerald-800",
  },
  red: {
    bg: "bg-red-50 dark:bg-red-950/30",
    icon: "bg-red-100 dark:bg-red-900/50",
    iconText: "text-red-600 dark:text-red-400",
    text: "text-red-700 dark:text-red-300",
    border: "border-red-200 dark:border-red-800",
  },
}

export function TicketStatus({ ticket }: TicketStatusProps) {
  const [isRefreshing, setIsRefreshing] = useState(false)

  const status = statusConfig[ticket.status]
  const StatusIcon = status.icon
  const colors = colorClasses[status.color as keyof typeof colorClasses]

  const copyTicketId = () => {
    navigator.clipboard.writeText(ticket.ticket_id)
    toast.success("Ticket ID copied to clipboard")
  }

  const refreshStatus = async () => {
    setIsRefreshing(true)
    await new Promise((resolve) => setTimeout(resolve, 1000))
    setIsRefreshing(false)
    toast.info("Ticket status refreshed")
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Header Card */}
      <Card className="overflow-hidden">
        <CardHeader className="border-b bg-muted/30">
          <div className="flex items-start justify-between">
            <div>
              <CardDescription className="flex items-center gap-2">
                <Sparkles className="h-3 w-3 text-primary" />
                Ticket ID
              </CardDescription>
              <div className="mt-1 flex items-center gap-2">
                <code className="font-mono text-lg font-semibold gradient-text">
                  {ticket.ticket_id.slice(0, 8)}...
                </code>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={copyTicketId}
                  className="h-8 w-8 hover:text-primary"
                  aria-label="Copy full ticket ID"
                >
                  <Copy className="h-4 w-4" />
                </Button>
              </div>
            </div>
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Button
                variant="outline"
                size="sm"
                onClick={refreshStatus}
                disabled={isRefreshing}
                className="rounded-full"
              >
                <RefreshCw
                  className={cn("mr-2 h-4 w-4", isRefreshing && "animate-spin")}
                />
                Refresh
              </Button>
            </motion.div>
          </div>
        </CardHeader>
        <CardContent className="pt-6">
          {/* Status Banner */}
          <div className={cn("rounded-2xl p-5 border", colors.bg, colors.border)}>
            <div className="flex items-center gap-4">
              <div className={cn("flex h-12 w-12 items-center justify-center rounded-xl", colors.icon)}>
                <StatusIcon className={cn("h-6 w-6", colors.iconText)} />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <Badge variant={status.variant}>{status.label}</Badge>
                  <Badge variant={priorityConfig[ticket.priority].variant}>
                    {priorityConfig[ticket.priority].label} Priority
                  </Badge>
                </div>
                <p className={cn("text-sm", colors.text)}>
                  {status.description}
                </p>
              </div>
            </div>

            {/* Progress bar */}
            <div className="mt-4">
              <div className="flex justify-between text-xs text-muted-foreground mb-2">
                <span>Progress</span>
                <span>{status.progress}%</span>
              </div>
              <Progress value={status.progress} className="h-2" />
            </div>
          </div>

          {/* Ticket Details */}
          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            {[
              { label: "Created", value: formatDate(ticket.created_at) },
              { label: "Category", value: ticket.category, capitalize: true },
              { label: "Channel", value: ticket.source_channel, capitalize: true },
              ...(ticket.resolved_at
                ? [{ label: "Resolved", value: formatDate(ticket.resolved_at) }]
                : []),
            ].map((item) => (
              <div key={item.label} className="rounded-xl bg-muted/50 p-3">
                <p className="text-xs text-muted-foreground font-medium uppercase tracking-wider">{item.label}</p>
                <p className={cn("font-semibold mt-0.5", item.capitalize && "capitalize")}>{item.value}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Conversation History */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-gradient-to-br from-primary/10 to-accent/10">
              <MessageSquare className="h-5 w-5 text-primary" />
            </div>
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
                <motion.div
                  key={message.id || index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className={cn(
                    "flex gap-3",
                    message.role === "customer" ? "flex-row" : "flex-row-reverse"
                  )}
                >
                  <Avatar className={cn(
                    "h-8 w-8",
                    message.role !== "customer" && "ring-2 ring-primary/20"
                  )}>
                    <AvatarFallback className={cn(
                      message.role === "customer"
                        ? "bg-muted"
                        : message.role === "agent"
                          ? "bg-gradient-to-br from-primary to-accent text-white"
                          : "bg-muted"
                    )}>
                      {message.role === "customer" ? (
                        <User className="h-4 w-4" />
                      ) : message.role === "agent" ? (
                        <Bot className="h-4 w-4" />
                      ) : (
                        <AlertCircle className="h-4 w-4 text-muted-foreground" />
                      )}
                    </AvatarFallback>
                  </Avatar>
                  <div
                    className={cn(
                      "max-w-[80%] rounded-2xl px-4 py-2.5 shadow-sm",
                      message.role === "customer"
                        ? "message-bubble-user"
                        : message.role === "agent"
                          ? "bg-muted rounded-tr-sm"
                          : "bg-yellow-50 dark:bg-yellow-950/30 border border-yellow-200 dark:border-yellow-800 rounded-tr-sm"
                    )}
                  >
                    <p className="text-sm leading-relaxed">{message.content}</p>
                    <p
                      className={cn(
                        "mt-1 text-[10px]",
                        message.role === "customer"
                          ? "text-white/70"
                          : "text-muted-foreground"
                      )}
                    >
                      {formatRelativeTime(message.created_at)}
                      {message.channel && ` via ${message.channel}`}
                    </p>
                  </div>
                </motion.div>
              ))}
            </div>
          ) : (
            <div className="py-12 text-center">
              <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-primary/10 to-accent/10">
                <MessageSquare className="h-8 w-8 text-primary" />
              </div>
              <p className="text-muted-foreground font-medium">
                No messages yet. Our agent will respond shortly.
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Help Section */}
      <Card className="border-dashed hover:border-primary/30 transition-colors">
        <CardContent className="pt-6">
          <div className="flex items-start gap-4">
            <div className="p-2 rounded-xl bg-gradient-to-br from-primary/10 to-accent/10 shrink-0">
              <AlertCircle className="h-5 w-5 text-primary" />
            </div>
            <div>
              <p className="font-semibold">Need more help?</p>
              <p className="mt-1 text-sm text-muted-foreground leading-relaxed">
                If your issue hasn't been resolved or you need to add more
                information, you can reply to the email response or submit a new
                request referencing this ticket ID.
              </p>
              <div className="mt-4 flex flex-wrap gap-2">
                <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                  <Button variant="outline" size="sm" asChild className="rounded-full">
                    <a href="/support">
                      Submit New Request
                      <ArrowRight className="ml-2 h-3 w-3" />
                    </a>
                  </Button>
                </motion.div>
                <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                  <Button variant="outline" size="sm" asChild className="rounded-full">
                    <a href="/chat">
                      Live Chat
                      <MessageSquare className="ml-2 h-3 w-3" />
                    </a>
                  </Button>
                </motion.div>
                <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                  <Button variant="outline" size="sm" asChild className="rounded-full">
                    <a href="mailto:support@company.com">Email Support</a>
                  </Button>
                </motion.div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
