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
      className="space-y-6 pb-12"
    >
      {/* Header Card */}
      <Card className="overflow-hidden border-none shadow-2xl glass-morphism ring-1 ring-white/20">
        <CardHeader className="border-b border-white/10 bg-white/5">
          <div className="flex items-start justify-between">
            <div>
              <CardDescription className="flex items-center gap-2 text-primary font-medium">
                <Sparkles className="h-3 w-3" />
                Support Ticket
              </CardDescription>
              <div className="mt-1 flex items-center gap-3">
                <code className="font-mono text-2xl font-bold gradient-text tracking-tighter">
                  #{ticket.ticket_id.slice(0, 8)}
                </code>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={copyTicketId}
                  className="h-8 w-8 hover:bg-primary/10 hover:text-primary transition-colors"
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
                className="rounded-full bg-white/5 border-white/10 backdrop-blur-sm"
              >
                <RefreshCw
                  className={cn("mr-2 h-4 w-4", isRefreshing && "animate-spin")}
                />
                Sync Status
              </Button>
            </motion.div>
          </div>
        </CardHeader>
        <CardContent className="pt-8">
          {/* Status Banner */}
          <div className={cn("rounded-3xl p-6 border shadow-inner relative overflow-hidden", colors.bg, colors.border)}>
            <div className="absolute top-0 right-0 w-32 h-32 -mr-16 -mt-16 bg-white/10 rounded-full blur-2xl" />
            <div className="relative z-10 flex items-center gap-6">
              <div className={cn("flex h-16 w-16 items-center justify-center rounded-2xl shadow-lg", colors.icon)}>
                <StatusIcon className={cn("h-8 w-8", colors.iconText)} />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <Badge variant={status.variant} className="px-3 py-1 rounded-full uppercase tracking-wider text-[10px] font-bold">
                    {status.label}
                  </Badge>
                  <Badge variant={priorityConfig[ticket.priority].variant} className="px-3 py-1 rounded-full uppercase tracking-wider text-[10px] font-bold">
                    {priorityConfig[ticket.priority].label} Priority
                  </Badge>
                </div>
                <h3 className={cn("text-lg font-bold", colors.iconText)}>
                  {status.description}
                </h3>
              </div>
            </div>

            {/* Progress bar */}
            <div className="mt-6 relative z-10">
              <div className="flex justify-between text-[10px] font-bold uppercase tracking-widest text-muted-foreground mb-2">
                <span>Resolution Progress</span>
                <span className={colors.iconText}>{status.progress}%</span>
              </div>
              <div className="h-3 w-full bg-black/5 dark:bg-white/5 rounded-full overflow-hidden">
                <motion.div 
                  initial={{ width: 0 }}
                  animate={{ width: `${status.progress}%` }}
                  transition={{ duration: 1, ease: "easeOut" }}
                  className={cn("h-full rounded-full shadow-lg", colors.icon)}
                />
              </div>
            </div>
          </div>

          {/* Ticket Details */}
          <div className="mt-8 grid gap-4 sm:grid-cols-3">
            {[
              { label: "Created", value: formatDate(ticket.created_at), icon: Clock },
              { label: "Category", value: ticket.category, icon: Sparkles, capitalize: true },
              { label: "Source", value: ticket.source_channel, icon: MessageSquare, capitalize: true },
            ].map((item) => (
              <div key={item.label} className="rounded-2xl bg-white/5 dark:bg-black/20 border border-white/5 p-4 transition-all hover:bg-white/10">
                <div className="flex items-center gap-2 mb-2">
                  <item.icon className="h-3 w-3 text-primary" />
                  <p className="text-[10px] text-muted-foreground font-bold uppercase tracking-widest">{item.label}</p>
                </div>
                <p className={cn("font-semibold text-sm", item.capitalize && "capitalize")}>{item.value}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Conversation History */}
      <Card className="border-none shadow-2xl glass-morphism ring-1 ring-white/20">
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-3 text-xl">
            <div className="p-2 rounded-xl bg-gradient-to-br from-primary/10 to-accent/10">
              <MessageSquare className="h-5 w-5 text-primary" />
            </div>
            Activity Logs
          </CardTitle>
          <CardDescription className="ml-12 font-medium">
            {ticket.messages?.length || 0} secure messages stored
          </CardDescription>
        </CardHeader>
        <CardContent className="pt-4">
          {ticket.messages && ticket.messages.length > 0 ? (
            <div className="space-y-6 relative">
              {/* Vertical timeline line */}
              <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-muted/30 -z-0" />
              
              {ticket.messages.map((message, index) => (
                <motion.div
                  key={message.id || index}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex gap-4 relative z-10"
                >
                  <Avatar className={cn(
                    "h-8 w-8 ring-4 ring-background",
                    message.role !== "customer" && "ring-primary/10"
                  )}>
                    <AvatarFallback className={cn(
                      "text-[10px] font-bold",
                      message.role === "customer"
                        ? "bg-muted"
                        : "bg-gradient-to-br from-primary to-accent text-white"
                    )}>
                      {message.role === "customer" ? "YOU" : "AI"}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold uppercase tracking-widest text-muted-foreground">
                        {message.role === "customer" ? "Your Request" : "AI Response"}
                      </span>
                      <span className="text-[10px] font-medium text-muted-foreground bg-muted/50 px-2 py-0.5 rounded-full">
                        {formatRelativeTime(message.created_at)}
                      </span>
                    </div>
                    <div
                      className={cn(
                        "rounded-2xl px-5 py-4 shadow-sm border transition-all duration-300",
                        message.role === "customer"
                          ? "bg-white/5 border-white/10"
                          : "bg-gradient-to-br from-primary/5 to-accent/5 border-primary/10"
                      )}
                    >
                      <p className="text-sm leading-relaxed tracking-wide">{message.content}</p>
                    </div>
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
