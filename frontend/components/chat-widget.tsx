"use client"

import { useState, useRef, useEffect } from "react"
import { toast } from "sonner"
import {
  Send,
  Bot,
  User,
  Loader2,
  Minimize2,
  Maximize2,
  X,
  Sparkles,
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

interface Message {
  id: string
  role: "user" | "assistant" | "system"
  content: string
  timestamp: Date
}

interface ChatWidgetProps {
  fullPage?: boolean
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

const suggestedQuestions = [
  "How do I reset my password?",
  "What are your business hours?",
  "How can I track my order?",
  "I need help with billing",
]

export function ChatWidget({ fullPage = false }: ChatWidgetProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Hello! I'm your AI support assistant. How can I help you today? You can ask me anything about our products or services.",
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isMinimized, setIsMinimized] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: content.trim(),
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    try {
      // In production, this would call your agent API
      // For now, we'll simulate a response
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: content,
          conversation_history: messages.map((m) => ({
            role: m.role,
            content: m.content,
          })),
        }),
      }).catch(() => null)

      let assistantContent: string

      if (response && response.ok) {
        const data = await response.json()
        assistantContent = data.response || data.message
      } else {
        // Fallback simulated response for demo
        assistantContent = getSimulatedResponse(content)
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: assistantContent,
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      toast.error("Failed to send message. Please try again.")
    } finally {
      setIsLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    sendMessage(input)
  }

  const handleSuggestedQuestion = (question: string) => {
    sendMessage(question)
  }

  // Simulated response for demo purposes
  function getSimulatedResponse(userMessage: string): string {
    const lowerMessage = userMessage.toLowerCase()

    if (lowerMessage.includes("password") || lowerMessage.includes("reset")) {
      return "To reset your password, please follow these steps:\n\n1. Go to the login page\n2. Click on 'Forgot Password'\n3. Enter your email address\n4. Check your inbox for a reset link\n5. Follow the link to create a new password\n\nIf you don't receive the email within 5 minutes, please check your spam folder. Would you like me to help with anything else?"
    }

    if (lowerMessage.includes("hours") || lowerMessage.includes("open")) {
      return "Our business hours are:\n\n• Monday - Friday: 9:00 AM - 6:00 PM (EST)\n• Saturday: 10:00 AM - 4:00 PM (EST)\n• Sunday: Closed\n\nHowever, our AI support is available 24/7 for general inquiries! Is there anything else I can help you with?"
    }

    if (lowerMessage.includes("track") || lowerMessage.includes("order")) {
      return "To track your order:\n\n1. Log into your account\n2. Go to 'My Orders'\n3. Click on the order you want to track\n4. You'll see the current status and tracking number\n\nAlternatively, you can use the tracking number in the shipping confirmation email. Do you need help with anything else?"
    }

    if (lowerMessage.includes("billing") || lowerMessage.includes("payment")) {
      return "I understand you have a billing question. For security reasons, billing inquiries involving sensitive information should be handled by our human support team.\n\nI've created a high-priority ticket for you. Our billing team will reach out within 15 minutes during business hours.\n\nIn the meantime, you can review your billing history in your account settings. Is there anything else I can help with?"
    }

    if (lowerMessage.includes("hello") || lowerMessage.includes("hi")) {
      return "Hello! Great to meet you! I'm here to help with any questions you might have. Feel free to ask about:\n\n• Account issues\n• Product information\n• Order tracking\n• General inquiries\n\nWhat can I assist you with today?"
    }

    if (lowerMessage.includes("thank")) {
      return "You're very welcome! I'm glad I could help. If you have any more questions in the future, don't hesitate to reach out. Have a great day! 😊"
    }

    return "Thank you for your message! I'm analyzing your request to provide the best possible assistance.\n\nBased on what you've shared, I'd recommend:\n\n1. Checking our FAQ section for quick answers\n2. Reviewing your account dashboard for relevant information\n3. If this is urgent, I can escalate to our human support team\n\nCould you provide more details about what you need help with? This will help me assist you better."
  }

  if (!fullPage && isMinimized) {
    return (
      <Button
        onClick={() => setIsMinimized(false)}
        className="fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-lg"
        size="icon"
      >
        <Bot className="h-6 w-6" />
      </Button>
    )
  }

  const containerClasses = fullPage
    ? "flex flex-col h-[calc(100vh-12rem)]"
    : "fixed bottom-6 right-6 w-[400px] h-[600px] flex flex-col rounded-lg border bg-card shadow-2xl"

  return (
    <div className={containerClasses}>
      {/* Header */}
      <div className="flex items-center justify-between border-b bg-primary px-4 py-3 text-primary-foreground rounded-t-lg">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-accent">
            <Sparkles className="h-4 w-4 text-primary" />
          </div>
          <div>
            <p className="font-medium">AI Support Assistant</p>
            <p className="text-xs text-primary-foreground/70">
              {isLoading ? "Typing..." : "Online"}
            </p>
          </div>
        </div>
        {!fullPage && (
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-primary-foreground hover:bg-primary-foreground/10"
              onClick={() => setIsMinimized(true)}
            >
              <Minimize2 className="h-4 w-4" />
            </Button>
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={cn(
              "flex gap-2",
              message.role === "user" ? "flex-row-reverse" : "flex-row"
            )}
          >
            <div
              className={cn(
                "flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
                message.role === "user" ? "bg-primary" : "bg-accent"
              )}
            >
              {message.role === "user" ? (
                <User className="h-4 w-4 text-primary-foreground" />
              ) : (
                <Bot className="h-4 w-4 text-primary" />
              )}
            </div>
            <div
              className={cn(
                "max-w-[80%] rounded-lg px-4 py-2",
                message.role === "user"
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted"
              )}
            >
              <p className="text-sm whitespace-pre-wrap">{message.content}</p>
              <p
                className={cn(
                  "mt-1 text-xs",
                  message.role === "user"
                    ? "text-primary-foreground/70"
                    : "text-muted-foreground"
                )}
              >
                {message.timestamp.toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </p>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-accent">
              <Bot className="h-4 w-4 text-primary" />
            </div>
            <div className="rounded-lg bg-muted px-4 py-3">
              <div className="flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="text-sm text-muted-foreground">Thinking...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Questions (only show if few messages) */}
      {messages.length <= 2 && !isLoading && (
        <div className="border-t px-4 py-3">
          <p className="text-xs text-muted-foreground mb-2">
            Suggested questions:
          </p>
          <div className="flex flex-wrap gap-2">
            {suggestedQuestions.map((question) => (
              <Badge
                key={question}
                variant="secondary"
                className="cursor-pointer hover:bg-accent hover:text-primary transition-colors"
                onClick={() => handleSuggestedQuestion(question)}
              >
                {question}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <form onSubmit={handleSubmit} className="border-t p-4">
        <div className="flex gap-2">
          <Input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            disabled={isLoading}
            className="flex-1"
          />
          <Button type="submit" disabled={isLoading || !input.trim()}>
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
        <p className="mt-2 text-center text-xs text-muted-foreground">
          Powered by AI • Available 24/7
        </p>
      </form>
    </div>
  )
}
