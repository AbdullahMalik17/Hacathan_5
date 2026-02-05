"use client"

import { ChatWidget } from "@/components/chat-widget"
import { Badge } from "@/components/ui/badge"
import { MessageCircle, Zap, Brain, Clock, Shield, Sparkles } from "lucide-react"
import { FadeIn, FadeInView, motion } from "@/components/motion"

const features = [
  {
    icon: Zap,
    title: "Instant Responses",
    description: "No waiting in queue. Get answers immediately.",
    gradient: "from-amber-400 to-orange-500",
  },
  {
    icon: Brain,
    title: "Smart AI",
    description: "Trained on our entire knowledge base for accurate answers.",
    gradient: "from-blue-500 to-indigo-600",
  },
  {
    icon: Clock,
    title: "24/7 Available",
    description: "Support whenever you need it, day or night.",
    gradient: "from-emerald-400 to-teal-500",
  },
  {
    icon: Shield,
    title: "Secure & Private",
    description: "All conversations are encrypted end-to-end.",
    gradient: "from-purple-500 to-pink-500",
  },
]

export default function ChatPage() {
  return (
    <div className="min-h-[calc(100vh-4rem)]">
      {/* Hero Section */}
      <section className="relative border-b overflow-hidden hero-bg py-12">
        {/* Background elements */}
        <div className="blob blob-1 w-60 h-60 -top-20 -right-20 opacity-30" />
        <div className="blob blob-2 w-40 h-40 bottom-0 left-0 opacity-20" />

        <div className="container relative">
          <div className="mx-auto max-w-3xl text-center">
            <FadeIn delay={0} direction="down">
              <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-primary to-accent shadow-lg shadow-primary/30">
                <MessageCircle className="h-8 w-8 text-white" />
              </div>
            </FadeIn>

            <FadeIn delay={0.1} direction="up">
              <h1 className="font-display text-3xl font-bold tracking-tight md:text-4xl">
                <span className="text-foreground">Live Chat</span>{" "}
                <span className="gradient-text">Support</span>
              </h1>
            </FadeIn>

            <FadeIn delay={0.2} direction="up">
              <p className="mt-3 text-muted-foreground text-lg">
                Chat with our AI assistant for instant help. No waiting required.
              </p>
            </FadeIn>

            {/* Feature Pills */}
            <FadeIn delay={0.3} direction="up">
              <div className="mt-6 flex flex-wrap justify-center gap-3">
                {features.map((feature, index) => (
                  <motion.div
                    key={feature.title}
                    whileHover={{ scale: 1.05, y: -2 }}
                    className="flex items-center gap-2 rounded-full border bg-card/50 backdrop-blur-sm px-4 py-2 text-sm shadow-sm hover:shadow-md transition-shadow"
                  >
                    <div className={`flex h-6 w-6 items-center justify-center rounded-full bg-gradient-to-br ${feature.gradient}`}>
                      <feature.icon className="h-3 w-3 text-white" />
                    </div>
                    <span className="font-medium">{feature.title}</span>
                  </motion.div>
                ))}
              </div>
            </FadeIn>
          </div>
        </div>
      </section>

      {/* Chat Section */}
      <section className="py-8">
        <div className="container">
          <div className="mx-auto max-w-4xl">
            <FadeInView direction="up">
              <div className="rounded-2xl border bg-card shadow-xl shadow-primary/5 overflow-hidden">
                <ChatWidget fullPage />
              </div>
            </FadeInView>

            {/* Tips */}
            <FadeInView delay={0.2} direction="up">
              <div className="mt-6 rounded-2xl border border-dashed bg-muted/30 p-6">
                <div className="flex items-center gap-2 mb-3">
                  <Sparkles className="h-4 w-4 text-primary" />
                  <h3 className="font-semibold">Tips for better support:</h3>
                </div>
                <div className="grid sm:grid-cols-3 gap-4">
                  <div className="flex items-start gap-2">
                    <div className="mt-1 h-1.5 w-1.5 rounded-full bg-primary shrink-0" />
                    <p className="text-sm text-muted-foreground">Be specific about your issue for faster resolution</p>
                  </div>
                  <div className="flex items-start gap-2">
                    <div className="mt-1 h-1.5 w-1.5 rounded-full bg-accent shrink-0" />
                    <p className="text-sm text-muted-foreground">Include any error messages or order numbers</p>
                  </div>
                  <div className="flex items-start gap-2">
                    <div className="mt-1 h-1.5 w-1.5 rounded-full bg-emerald-500 shrink-0" />
                    <p className="text-sm text-muted-foreground">Complex issues are automatically escalated to human support</p>
                  </div>
                </div>
              </div>
            </FadeInView>
          </div>
        </div>
      </section>
    </div>
  )
}
