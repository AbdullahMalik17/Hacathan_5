"use client"

import { Metadata } from "next"
import { SupportForm } from "@/components/support-form"
import { Mail, MessageCircle, Globe, Clock, Zap, Shield, Sparkles, ChevronRight, HelpCircle } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { Progress } from "@/components/ui/progress"
import { FadeIn, FadeInView, StaggerContainer, StaggerItem, motion } from "@/components/motion"

const features = [
  {
    icon: Zap,
    title: "Instant AI Responses",
    description: "Our AI agent processes your request and responds within minutes.",
    gradient: "from-sky-500 to-blue-600",
  },
  {
    icon: Clock,
    title: "24/7 Availability",
    description: "Support available round the clock, every day of the year.",
    gradient: "from-blue-500 to-indigo-500",
  },
  {
    icon: Shield,
    title: "Secure & Private",
    description: "Your data is encrypted and handled with care.",
    gradient: "from-emerald-500 to-teal-500",
  },
]

const channels = [
  {
    icon: Mail,
    title: "Email",
    description: "support@company.com",
    responseTime: "Within 5 minutes",
    gradient: "from-blue-500 to-indigo-500",
    progress: 95,
  },
  {
    icon: MessageCircle,
    title: "WhatsApp",
    description: "+1 (555) 123-4567",
    responseTime: "Within 2 minutes",
    gradient: "from-emerald-500 to-teal-500",
    progress: 98,
  },
  {
    icon: Globe,
    title: "Web Form",
    description: "Submit below",
    responseTime: "Within 5 minutes",
    gradient: "from-purple-500 to-pink-500",
    progress: 95,
  },
]

const faqItems = [
  {
    question: "What are your response times?",
    answer: "Our AI agent typically responds within 2-5 minutes for all channels. High-priority requests are handled first. During peak hours, response times may be slightly longer, but we always aim to respond as quickly as possible.",
  },
  {
    question: "Can I track my support ticket?",
    answer: "Yes! After submitting a request, you'll receive a unique ticket ID. You can use this ID to track the status of your request anytime through our ticket tracking page. You'll also receive email updates as your ticket progresses.",
  },
  {
    question: "Will I talk to a human?",
    answer: "Our AI handles most requests efficiently and accurately. However, complex issues are automatically escalated to our human support team. You can also request human assistance at any time during your conversation.",
  },
  {
    question: "Is my data secure?",
    answer: "Absolutely. All communications are encrypted using bank-grade encryption (AES-256). We follow strict data protection guidelines including GDPR compliance. Your data is never shared with third parties.",
  },
  {
    question: "What issues can the AI help with?",
    answer: "Our AI assistant can help with account issues, password resets, order tracking, billing questions, product information, technical troubleshooting, and general inquiries. For sensitive matters, we'll connect you with a human agent.",
  },
  {
    question: "How do I escalate to a human agent?",
    answer: "Simply type 'speak to human' or 'escalate' in the chat, or select 'High Priority' when submitting a ticket. Our system will automatically route your request to an available human agent.",
  },
]

export default function SupportPage() {
  return (
    <div className="min-h-[calc(100vh-4rem)] relative">
      {/* Background blobs specific to this page */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none -z-10">
        <div className="aura-glow top-[-5%] left-[10%] bg-sky-500/10" />
        <div className="aura-glow bottom-[20%] right-[10%] bg-emerald-500/10" />
      </div>

      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="container relative py-20 md:py-28">
          <StaggerContainer className="mx-auto max-w-3xl text-center">
            {/* Badge */}
            <StaggerItem delay={0} direction="down">
              <Badge className="mb-6 py-1.5 px-4 rounded-full bg-primary/10 text-primary border-primary/20 shadow-sm">
                <Sparkles className="h-3.5 w-3.5 mr-2" />
                <span className="font-bold tracking-tight uppercase text-[10px]">AI-Powered Support HUB</span>
              </Badge>
            </StaggerItem>

            <StaggerItem delay={0.1}>
              <h1 className="font-display text-5xl font-bold tracking-tight md:text-6xl lg:text-7xl">
                <span className="text-foreground">How can we</span>
                <br />
                <span className="gradient-text">help you today?</span>
              </h1>
            </StaggerItem>

            <StaggerItem delay={0.2}>
              <p className="mt-8 text-xl text-muted-foreground md:text-2xl max-w-2xl mx-auto leading-relaxed">
                Get instant, accurate responses from our support team, available{" "}
                <span className="text-primary font-bold">24/7</span> round the clock.
              </p>
            </StaggerItem>
          </StaggerContainer>

          {/* Feature cards */}
          <StaggerContainer className="mt-20 grid gap-8 md:grid-cols-3">
            {features.map((feature, index) => (
              <StaggerItem key={feature.title} delay={0.3 + index * 0.1}>
                <motion.div
                  whileHover={{ y: -8, scale: 1.02 }}
                  className="feature-card group glass-morphism border-none shadow-xl ring-1 ring-white/10"
                >
                  <div className={`mb-6 inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br ${feature.gradient} shadow-lg shadow-primary/20 group-hover:scale-110 transition-all duration-300`}>
                    <feature.icon className="h-7 w-7 text-white" />
                  </div>
                  <h3 className="font-display text-xl font-bold mb-3">{feature.title}</h3>
                  <p className="text-muted-foreground leading-relaxed">{feature.description}</p>
                </motion.div>
              </StaggerItem>
            ))}
          </StaggerContainer>
        </div>
      </section>

      {/* Main Content */}
      <section className="py-16 md:py-24">
        <div className="container">
          <div className="grid gap-16 lg:grid-cols-3">
            {/* Support Form */}
            <div className="lg:col-span-2">
              <FadeInView direction="up">
                <Tabs defaultValue="form" className="w-full">
                  <TabsList className="grid w-full grid-cols-2 p-1 bg-muted/50 rounded-2xl h-14 mb-10 shadow-inner">
                    <TabsTrigger value="form" className="rounded-xl font-bold text-sm uppercase tracking-wider data-[state=active]:bg-white dark:data-[state=active]:bg-black data-[state=active]:shadow-lg">
                      Submit Ticket
                    </TabsTrigger>
                    <TabsTrigger value="chat" className="rounded-xl font-bold text-sm uppercase tracking-wider data-[state=active]:bg-white dark:data-[state=active]:bg-black data-[state=active]:shadow-lg">
                      Live Concierge
                    </TabsTrigger>
                  </TabsList>
                  <TabsContent value="form">
                    <SupportForm />
                  </TabsContent>
                  <TabsContent value="chat">
                    <div className="rounded-3xl border-none glass-morphism p-12 text-center shadow-2xl ring-1 ring-white/20">
                      <div className="mx-auto mb-8 flex h-24 w-24 items-center justify-center rounded-3xl bg-gradient-to-br from-primary to-accent shadow-2xl shadow-primary/30 ring-4 ring-primary/10">
                        <MessageCircle className="h-12 w-12 text-white" />
                      </div>
                      <h3 className="font-display text-3xl font-bold mb-4">Start a Live Chat</h3>
                      <p className="text-muted-foreground text-lg mb-10 max-w-md mx-auto">
                        Get instant help from our AI assistant. Available 24/7 for all your needs.
                      </p>
                      <motion.a
                        href="/chat"
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className="inline-flex items-center justify-center gap-3 rounded-full btn-gradient px-10 py-4 text-white font-bold text-lg shadow-xl"
                      >
                        Launch Chat
                        <ChevronRight className="h-5 w-5" />
                      </motion.a>
                    </div>
                  </TabsContent>
                </Tabs>
              </FadeInView>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Contact Channels */}
              <FadeInView delay={0.1} direction="left">
                <div className="rounded-2xl border bg-card p-6 shadow-sm">
                  <h3 className="font-display text-lg font-semibold mb-6">
                    Other Ways to Reach Us
                  </h3>
                  <div className="space-y-4">
                    {channels.map((channel) => (
                      <motion.div
                        key={channel.title}
                        whileHover={{ x: 5 }}
                        className="group flex gap-4 rounded-xl p-3 transition-colors hover:bg-muted/50 cursor-pointer"
                      >
                        <div className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br ${channel.gradient} shadow-lg shadow-primary/10 group-hover:scale-105 transition-transform`}>
                          <channel.icon className="h-5 w-5 text-white" />
                        </div>
                        <div className="flex-1">
                          <p className="font-semibold">{channel.title}</p>
                          <p className="text-sm text-muted-foreground">
                            {channel.description}
                          </p>
                          <div className="mt-2 flex items-center gap-2">
                            <Progress value={channel.progress} className="h-1.5 flex-1" />
                            <span className="text-xs font-medium text-primary">
                              {channel.responseTime}
                            </span>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>
              </FadeInView>

              {/* FAQ */}
              <FadeInView delay={0.2} direction="left">
                <div className="rounded-2xl border bg-card p-6 shadow-sm">
                  <div className="flex items-center gap-2 mb-6">
                    <HelpCircle className="h-5 w-5 text-primary" />
                    <h3 className="font-display text-lg font-semibold">
                      Frequently Asked Questions
                    </h3>
                  </div>
                  <Accordion type="single" collapsible className="w-full">
                    {faqItems.map((item, index) => (
                      <AccordionItem key={index} value={`item-${index}`}>
                        <AccordionTrigger className="text-left text-sm font-medium hover:text-primary transition-colors">
                          {item.question}
                        </AccordionTrigger>
                        <AccordionContent className="text-sm text-muted-foreground leading-relaxed">
                          {item.answer}
                        </AccordionContent>
                      </AccordionItem>
                    ))}
                  </Accordion>
                </div>
              </FadeInView>

              {/* Status Indicator */}
              <FadeInView delay={0.3} direction="left">
                <motion.div
                  whileHover={{ scale: 1.02 }}
                  className="rounded-2xl border border-emerald-200 bg-gradient-to-br from-emerald-50 to-teal-50 dark:from-emerald-950/30 dark:to-teal-950/30 dark:border-emerald-800 p-6 shadow-sm"
                >
                  <div className="flex items-center gap-4">
                    <div className="relative">
                      <div className="h-4 w-4 rounded-full bg-emerald-500 shadow-lg shadow-emerald-500/50" />
                      <div className="absolute inset-0 h-4 w-4 animate-ping rounded-full bg-emerald-500 opacity-75" />
                    </div>
                    <div>
                      <p className="font-semibold text-emerald-900 dark:text-emerald-100">All Systems Operational</p>
                      <p className="text-sm text-emerald-700 dark:text-emerald-300">
                        Support is available 24/7
                      </p>
                    </div>
                  </div>
                </motion.div>
              </FadeInView>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
