"use client"

import { useState, useRef, useEffect } from "react"
import { toast } from "sonner"
import {
  Send,
  Bot,
  User,
  Loader2,
  Minimize2,
  X,
  Sparkles,
  ThumbsUp,
  ThumbsDown,
  Copy,
  RotateCcw,
  Mic,
  Paperclip,
} from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import { ScrollArea } from "@/components/ui/scroll-area"
import { cn } from "@/lib/utils"
import { motion, AnimatePresence } from "framer-motion"

interface Message {
  id: string
  role: "user" | "assistant" | "system"
  content: string
  timestamp: Date
  reaction?: "like" | "dislike"
}

interface ChatWidgetProps {
  fullPage?: boolean
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || ""

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
        "Hello! I'm your AI Concierge. I can help with account issues, orders, or general questions.",
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [loadingText, setLoadingText] = useState("Thinking...")
  const [isMinimized, setIsMinimized] = useState(false)
  const [showSuggestions, setShowSuggestions] = useState(true)

  useEffect(() => {
    let interval: NodeJS.Timeout
    if (isLoading) {
      const texts = ["Analyzing request...", "Searching knowledge base...", "Drafting response...", "Thinking..."]
      let i = 0
      interval = setInterval(() => {
        setLoadingText(texts[i % texts.length])
        i++
      }, 800)
    }
    return () => clearInterval(interval)
  }, [isLoading])

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    if (messages.length > 2) {
      setShowSuggestions(false)
    }
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
    setShowSuggestions(false)

    try {
      let assistantContent: string

      if (API_BASE_URL) {
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

        if (response && response.ok) {
          const data = await response.json()
          assistantContent = data.response || data.message
        } else {
          assistantContent = getSimulatedResponse(content)
          if (response && !response.ok) {
            toast.error("Backend unavailable. Showing demo response.")
          }
        }
      } else {
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

  const handleReaction = (messageId: string, reaction: "like" | "dislike") => {
    setMessages((prev) =>
      prev.map((m) =>
        m.id === messageId ? { ...m, reaction: m.reaction === reaction ? undefined : reaction } : m
      )
    )
    toast.success(reaction === "like" ? "Thanks for your feedback!" : "We'll work to improve!")
  }

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content)
    toast.success("Copied to clipboard!")
  }

  const clearChat = () => {
    setMessages([
      {
        id: "welcome-new",
        role: "assistant",
        content:
          "Hello! I'm your AI support assistant. How can I help you today?",
        timestamp: new Date(),
      },
    ])
    setShowSuggestions(true)
    toast.success("Chat cleared!")
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
      return "You're very welcome! I'm glad I could help. If you have any more questions in the future, don't hesitate to reach out. Have a great day!"
    }

    return "Thank you for your message! I'm analyzing your request to provide the best possible assistance.\n\nBased on what you've shared, I'd recommend:\n\n1. Checking our FAQ section for quick answers\n2. Reviewing your account dashboard for relevant information\n3. If this is urgent, I can escalate to our human support team\n\nCould you provide more details about what you need help with? This will help me assist you better."
  }

  if (!fullPage && isMinimized) {
    return (
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        className="fixed bottom-6 right-6 z-50"
      >
        <Button
          onClick={() => setIsMinimized(false)}
          className="h-14 w-14 rounded-full shadow-lg btn-gradient btn-glow"
          size="icon"
        >
          <Bot className="h-6 w-6" />
        </Button>
      </motion.div>
    )
  }

  const containerClasses = fullPage
    ? "flex flex-col h-[calc(100vh-12rem)] max-w-4xl mx-auto glass-morphism rounded-3xl overflow-hidden shadow-2xl ring-1 ring-white/20"
    : "fixed bottom-6 right-6 w-[420px] h-[650px] flex flex-col rounded-3xl border-none glass-morphism shadow-2xl z-50 overflow-hidden ring-1 ring-white/20"

  return (
    <motion.div
      initial={!fullPage ? { opacity: 0, y: 20, scale: 0.95 } : false}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      className={containerClasses}
    >
      {/* Header */}
      <div className="flex items-center justify-between bg-gradient-to-r from-primary/90 to-accent/90 backdrop-blur-md px-6 py-4 text-white shadow-lg">
        <div className="flex items-center gap-3">
          <div className="relative">
            <Avatar className="h-12 w-12 border-2 border-white/50 shadow-inner">
              <AvatarImage src="/ai-avatar.png" />
              <AvatarFallback className="bg-white/20 text-white">
                <Sparkles className="h-6 w-6" />
              </AvatarFallback>
            </Avatar>
            <span className="absolute bottom-0.5 right-0.5 h-3.5 w-3.5 rounded-full bg-emerald-400 border-2 border-white animate-pulse" />
          </div>
          <div>
            <p className="font-bold tracking-tight">AI Concierge</p>
            <p className="text-[10px] font-medium text-white/80 uppercase tracking-widest flex items-center gap-1.5">
              {isLoading ? loadingText : "Ready to help"}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 text-white hover:bg-white/10"
                onClick={clearChat}
              >
                <RotateCcw className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Clear chat</TooltipContent>
          </Tooltip>
          {!fullPage && (
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-white hover:bg-white/10"
              onClick={() => setIsMinimized(true)}
            >
              <Minimize2 className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 p-4">
        <AnimatePresence initial={false}>
          {messages.map((message, index) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
              className={cn(
                "flex gap-3 mb-4",
                message.role === "user" ? "flex-row-reverse" : "flex-row"
              )}
            >
              <Avatar className={cn(
                "h-8 w-8 shrink-0",
                message.role === "user" ? "" : "ring-2 ring-primary/20"
              )}>
                <AvatarFallback className={cn(
                  message.role === "user"
                    ? "bg-muted"
                    : "bg-gradient-to-br from-primary to-accent text-white"
                )}>
                  {message.role === "user" ? (
                    <User className="h-4 w-4" />
                  ) : (
                    <Bot className="h-4 w-4" />
                  )}
                </AvatarFallback>
              </Avatar>
              <div className={cn(
                "max-w-[75%] group",
                message.role === "user" ? "items-end" : "items-start"
              )}>
                <div
                  className={cn(
                    "rounded-2xl px-4 py-3 shadow-md transition-all duration-300",
                    message.role === "user"
                      ? "message-bubble-user"
                      : "bg-white/50 dark:bg-black/40 backdrop-blur-sm border border-white/20 rounded-tl-sm hover:bg-white/60 dark:hover:bg-black/50"
                  )}
                >
                  <p className="text-sm whitespace-pre-wrap leading-relaxed tracking-wide">{message.content}</p>
                </div>
                <div className={cn(
                  "flex items-center gap-2 mt-1.5 px-1",
                  message.role === "user" ? "justify-end" : "justify-start"
                )}>
                  <span className="text-[10px] text-muted-foreground">
                    {message.timestamp.toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                  {message.role === "assistant" && (
                    <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Button
                            variant="ghost"
                            size="icon"
                            className={cn(
                              "h-6 w-6",
                              message.reaction === "like" && "text-emerald-500"
                            )}
                            onClick={() => handleReaction(message.id, "like")}
                          >
                            <ThumbsUp className="h-3 w-3" />
                          </Button>
                        </TooltipTrigger>
                        <TooltipContent>Helpful</TooltipContent>
                      </Tooltip>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Button
                            variant="ghost"
                            size="icon"
                            className={cn(
                              "h-6 w-6",
                              message.reaction === "dislike" && "text-red-500"
                            )}
                            onClick={() => handleReaction(message.id, "dislike")}
                          >
                            <ThumbsDown className="h-3 w-3" />
                          </Button>
                        </TooltipTrigger>
                        <TooltipContent>Not helpful</TooltipContent>
                      </Tooltip>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6"
                            onClick={() => copyMessage(message.content)}
                          >
                            <Copy className="h-3 w-3" />
                          </Button>
                        </TooltipTrigger>
                        <TooltipContent>Copy</TooltipContent>
                      </Tooltip>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Typing Indicator */}
        <AnimatePresence>
          {isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="flex gap-3 mb-4"
            >
              <Avatar className="h-8 w-8 ring-2 ring-primary/20">
                <AvatarFallback className="bg-gradient-to-br from-primary to-accent text-white">
                  <Bot className="h-4 w-4" />
                </AvatarFallback>
              </Avatar>
              <div className="rounded-2xl rounded-tl-sm bg-muted px-4 py-3">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div ref={messagesEndRef} />
      </ScrollArea>

      {/* Suggested Questions */}
      <AnimatePresence>
        {showSuggestions && !isLoading && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="border-t px-4 py-3 bg-muted/30"
          >
            <p className="text-xs text-muted-foreground mb-2 font-medium">
              Suggested questions:
            </p>
            <div className="flex flex-wrap gap-2">
              {suggestedQuestions.map((question) => (
                <motion.div
                  key={question}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Badge
                    variant="secondary"
                    className="cursor-pointer hover:bg-primary hover:text-white transition-all duration-200 py-1.5 px-3"
                    onClick={() => handleSuggestedQuestion(question)}
                  >
                    {question}
                  </Badge>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Input */}
      <form onSubmit={handleSubmit} className="border-t p-4 bg-background">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Input
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              disabled={isLoading}
              className="pr-20 h-12 rounded-xl border-2 focus:border-primary/50 transition-colors input-focus-ring"
            />
            <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-muted-foreground hover:text-foreground"
                    disabled
                  >
                    <Paperclip className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Attach file (coming soon)</TooltipContent>
              </Tooltip>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-muted-foreground hover:text-foreground"
                    disabled
                  >
                    <Mic className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Voice input (coming soon)</TooltipContent>
              </Tooltip>
            </div>
          </div>
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="h-12 w-12 rounded-xl btn-gradient"
              size="icon"
            >
              {isLoading ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <Send className="h-5 w-5" />
              )}
            </Button>
          </motion.div>
        </div>
        <p className="mt-2 text-center text-[10px] text-muted-foreground">
          Powered by AI • Available 24/7 • Press Enter to send
        </p>
      </form>
    </motion.div>
  )
}
