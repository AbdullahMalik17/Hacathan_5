"use client"

import { ChatWidget } from "@/components/chat-widget"
import { Badge } from "@/components/ui/badge"
import { MessageCircle, Zap, Brain, Clock, Shield, Sparkles } from "lucide-react"
import { FadeIn, FadeInView, StaggerContainer, StaggerItem, motion } from "@/components/motion"

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
    <div className="min-h-[calc(100vh-4rem)] relative">
      {/* Background blobs specific to this page */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none -z-10">
        <div className="aura-glow top-[20%] right-[-5%] bg-blue-500/20" />
        <div className="aura-glow bottom-[10%] left-[-5%] bg-purple-500/20" />
      </div>

      {/* Hero Section */}
      <section className="relative overflow-hidden py-12">
        <div className="container relative">
          <StaggerContainer className="mx-auto max-w-3xl text-center">
            <StaggerItem delay={0} direction="down">
              <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-2xl bg-gradient-to-br from-primary to-accent shadow-xl shadow-primary/30 ring-4 ring-primary/10">
                <MessageCircle className="h-10 w-10 text-white" />
              </div>
            </StaggerItem>

            <StaggerItem delay={0.1}>
              <h1 className="font-display text-4xl font-bold tracking-tight md:text-5xl lg:text-6xl">
                <span className="text-foreground">Live AI</span>{" "}
                <span className="gradient-text">Concierge</span>
              </h1>
            </StaggerItem>

            <StaggerItem delay={0.2}>
              <p className="mt-4 text-muted-foreground text-xl leading-relaxed">
                Experience instant resolution with our advanced AI support system.
              </p>
            </StaggerItem>

            {/* Feature Pills */}
            <StaggerItem delay={0.3}>
              <div className="mt-8 flex flex-wrap justify-center gap-4">
                {features.map((feature, index) => (
                  <motion.div
                    key={feature.title}
                    whileHover={{ scale: 1.05, y: -2 }}
                    className="flex items-center gap-3 rounded-2xl border bg-card/40 backdrop-blur-md px-5 py-2.5 text-sm shadow-sm hover:shadow-xl hover:border-primary/30 transition-all duration-300"
                  >
                    <div className={`flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-br ${feature.gradient} shadow-lg shadow-black/5`}>
                      <feature.icon className="h-4 w-4 text-white" />
                    </div>
                    <span className="font-semibold">{feature.title}</span>
                  </motion.div>
                ))}
              </div>
            </StaggerItem>
          </StaggerContainer>
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
