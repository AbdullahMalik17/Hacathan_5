import { Metadata } from "next"
import { ChatWidget } from "@/components/chat-widget"
import { MessageCircle, Zap, Brain, Clock } from "lucide-react"

export const metadata: Metadata = {
  title: "Live Chat",
  description:
    "Chat with our AI-powered support assistant. Get instant answers to your questions 24/7.",
}

const features = [
  {
    icon: Zap,
    title: "Instant Responses",
    description: "No waiting in queue. Get answers immediately.",
  },
  {
    icon: Brain,
    title: "Smart AI",
    description: "Trained on our entire knowledge base for accurate answers.",
  },
  {
    icon: Clock,
    title: "24/7 Available",
    description: "Support whenever you need it, day or night.",
  },
]

export default function ChatPage() {
  return (
    <div className="min-h-[calc(100vh-4rem)]">
      {/* Hero Section */}
      <section className="border-b bg-gradient-to-b from-background to-muted/30 py-12">
        <div className="container">
          <div className="mx-auto max-w-3xl text-center">
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-accent/20">
              <MessageCircle className="h-8 w-8 text-accent" />
            </div>
            <h1 className="font-display text-3xl font-bold tracking-tight md:text-4xl">
              Live Chat Support
            </h1>
            <p className="mt-3 text-muted-foreground">
              Chat with our AI assistant for instant help. No waiting required.
            </p>

            {/* Feature Pills */}
            <div className="mt-6 flex flex-wrap justify-center gap-3">
              {features.map((feature) => (
                <div
                  key={feature.title}
                  className="flex items-center gap-2 rounded-full border bg-card px-4 py-2 text-sm"
                >
                  <feature.icon className="h-4 w-4 text-accent" />
                  <span>{feature.title}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Chat Section */}
      <section className="py-8">
        <div className="container">
          <div className="mx-auto max-w-3xl">
            <div className="rounded-lg border bg-card shadow-lg overflow-hidden">
              <ChatWidget fullPage />
            </div>

            {/* Tips */}
            <div className="mt-6 rounded-lg border border-dashed p-4">
              <h3 className="font-medium">Tips for better support:</h3>
              <ul className="mt-2 space-y-1 text-sm text-muted-foreground">
                <li>• Be specific about your issue for faster resolution</li>
                <li>• Include any error messages or order numbers if relevant</li>
                <li>• Our AI will escalate complex issues to human support automatically</li>
              </ul>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
