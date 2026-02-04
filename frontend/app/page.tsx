"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import {
  ArrowRight,
  MessageSquare,
  Zap,
  Shield,
  Clock,
  CheckCircle2,
  Bot,
  Users,
  Sparkles,
  Star,
  TrendingUp,
  Globe,
  Headphones,
  Heart,
} from "lucide-react"
import Link from "next/link"
import { FadeIn, FadeInView, StaggerContainer, StaggerItem, Float, ScaleOnHover, motion } from "@/components/motion"

const stats = [
  { value: "99.8%", label: "Resolution Rate", icon: CheckCircle2 },
  { value: "< 2min", label: "Avg. Response", icon: Zap },
  { value: "24/7", label: "Availability", icon: Clock },
  { value: "50K+", label: "Happy Customers", icon: Heart },
]

const features = [
  {
    icon: Bot,
    title: "AI-Powered Intelligence",
    description: "Our advanced AI understands context, sentiment, and technical details to provide accurate resolutions instantly.",
    gradient: "from-blue-500 to-indigo-600",
    delay: 0,
  },
  {
    icon: Clock,
    title: "24/7 Availability",
    description: "Support never sleeps. Whether it's 2 PM or 2 AM, our systems are awake and ready to assist you immediately.",
    gradient: "from-indigo-500 to-purple-600",
    delay: 0.1,
  },
  {
    icon: Shield,
    title: "Enterprise Security",
    description: "Bank-grade encryption and strict privacy protocols ensure your sensitive data remains protected at all times.",
    gradient: "from-emerald-400 to-teal-500",
    delay: 0.2,
  },
  {
    icon: TrendingUp,
    title: "Smart Escalation",
    description: "Complex issues are automatically escalated to human experts, ensuring you always get the best support.",
    gradient: "from-orange-400 to-rose-500",
    delay: 0.3,
  },
  {
    icon: Globe,
    title: "Multi-Channel Support",
    description: "Reach us via web, email, or WhatsApp. All channels are connected for a seamless experience.",
    gradient: "from-cyan-400 to-blue-500",
    delay: 0.4,
  },
  {
    icon: Headphones,
    title: "Personalized Experience",
    description: "Our AI remembers your history and preferences to provide tailored support every time.",
    gradient: "from-pink-400 to-purple-500",
    delay: 0.5,
  },
]

const testimonials = [
  {
    name: "Sarah Johnson",
    role: "Product Manager",
    company: "TechCorp",
    content: "The AI support is incredibly fast and accurate. It resolved my issue in under 2 minutes!",
    rating: 5,
  },
  {
    name: "Michael Chen",
    role: "Developer",
    company: "StartupXYZ",
    content: "Best support experience I've ever had. The AI understood my technical question perfectly.",
    rating: 5,
  },
  {
    name: "Emily Davis",
    role: "Operations Lead",
    company: "GlobalInc",
    content: "24/7 availability is a game-changer. No more waiting for business hours!",
    rating: 5,
  },
]

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen overflow-hidden">
      {/* Hero Section */}
      <section className="relative pt-20 pb-16 md:pt-32 md:pb-24 lg:pt-40 lg:pb-32 overflow-hidden">
        {/* Animated Background Elements */}
        <div className="absolute inset-0 overflow-hidden -z-10">
          {/* Floating particles */}
          <Float duration={4} distance={15} className="absolute top-[20%] left-[10%]">
            <div className="w-3 h-3 rounded-full bg-primary/30" />
          </Float>
          <Float duration={5} distance={20} className="absolute top-[60%] right-[15%]">
            <div className="w-4 h-4 rounded-full bg-accent/30" />
          </Float>
          <Float duration={6} distance={12} className="absolute bottom-[30%] left-[30%]">
            <div className="w-2 h-2 rounded-full bg-primary/40" />
          </Float>
        </div>

        <div className="container relative z-10">
          <div className="flex flex-col items-center text-center max-w-4xl mx-auto">
            {/* Status Badge */}
            <FadeIn delay={0} direction="down">
              <div className="flex items-center gap-2 px-4 py-2 rounded-full glass-card text-sm font-medium mb-8 shadow-lg">
                <span className="relative flex h-2 w-2">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500"></span>
                </span>
                <span className="gradient-text font-semibold">Next-Gen Support System</span>
                <Sparkles className="h-4 w-4 text-primary" />
              </div>
            </FadeIn>

            {/* Main Heading */}
            <FadeIn delay={0.1} direction="up">
              <h1 className="font-display text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight mb-6 leading-[1.1]">
                Customer Support
              </h1>
            </FadeIn>

            {/* Subtitle */}
            <FadeIn delay={0.2} direction="up">
              <p className="text-xl md:text-2xl text-muted-foreground mb-10 max-w-2xl leading-relaxed">
                Experience the perfect blend of{" "}
                <span className="text-primary font-semibold">AI speed</span> and{" "}
                <span className="text-accent font-semibold">human empathy</span>.
                Get instant answers, 24/7 availability, and seamless resolution.
              </p>
            </FadeIn>

            {/* CTA Buttons */}
            <FadeIn delay={0.3} direction="up">
              <div className="flex flex-col sm:flex-row items-center gap-4 w-full justify-center">
                <Link href="/chat">
                  <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.98 }}>
                    <Button size="lg" className="h-14 px-8 text-base rounded-full btn-gradient shadow-xl shadow-primary/30 group">
                      <MessageSquare className="mr-2 h-5 w-5 transition-transform group-hover:scale-110" />
                      Start Live Chat
                      <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
                    </Button>
                  </motion.div>
                </Link>
                <Link href="/support">
                  <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.98 }}>
                    <Button variant="outline" size="lg" className="h-14 px-8 text-base rounded-full border-2 hover:bg-muted/50 backdrop-blur-sm bg-background/50 group">
                      Submit Ticket
                      <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
                    </Button>
                  </motion.div>
                </Link>
              </div>
            </FadeIn>

            {/* Stats Row */}
            <FadeIn delay={0.4} direction="up" className="w-full">
              <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
                {stats.map((stat, index) => (
                  <motion.div
                    key={stat.label}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.5 + index * 0.1 }}
                  >
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <div className="stats-card group cursor-pointer hover:border-primary/30 transition-all duration-300 hover:-translate-y-1">
                          <div className="flex items-center gap-3 mb-2">
                            <div className="p-2 rounded-xl bg-gradient-to-br from-primary/10 to-accent/10 group-hover:from-primary/20 group-hover:to-accent/20 transition-colors">
                              <stat.icon className="h-5 w-5 text-primary" />
                            </div>
                          </div>
                          <p className="text-2xl md:text-3xl font-bold font-display gradient-text">{stat.value}</p>
                          <p className="text-sm text-muted-foreground">{stat.label}</p>
                        </div>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>Industry-leading {stat.label.toLowerCase()}</p>
                      </TooltipContent>
                    </Tooltip>
                  </motion.div>
                ))}
              </div>
            </FadeIn>

            {/* Floating UI Mockup */}
            <FadeIn delay={0.6} direction="up" className="w-full">
              <div className="relative mt-20 w-full max-w-4xl mx-auto">
                <ScaleOnHover scale={1.02}>
                  <div className="relative rounded-2xl border border-white/20 glass-card shadow-2xl p-2 md:p-4">
                    <div className="rounded-xl overflow-hidden bg-background border shadow-inner">
                      {/* Mock Interface Header */}
                      <div className="h-12 bg-muted/50 border-b flex items-center px-4 gap-2">
                        <div className="flex gap-1.5">
                          <div className="w-3 h-3 rounded-full bg-red-400/80 hover:bg-red-500 transition-colors cursor-pointer" />
                          <div className="w-3 h-3 rounded-full bg-yellow-400/80 hover:bg-yellow-500 transition-colors cursor-pointer" />
                          <div className="w-3 h-3 rounded-full bg-green-400/80 hover:bg-green-500 transition-colors cursor-pointer" />
                        </div>
                        <div className="mx-auto flex items-center gap-2">
                          <div className="w-4 h-4 rounded bg-primary/20" />
                          <div className="w-32 h-2 rounded-full bg-foreground/5" />
                        </div>
                      </div>
                      {/* Mock Content */}
                      <div className="p-6 md:p-10 grid md:grid-cols-2 gap-8 items-center">
                        <div className="space-y-4">
                          {/* AI Message */}
                          <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 1 }}
                            className="flex items-start gap-3"
                          >
                            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white shrink-0 shadow-lg">
                              <Bot className="h-5 w-5" />
                            </div>
                            <div className="space-y-2">
                              <div className="inline-flex items-center gap-2">
                                <span className="text-sm font-medium">AI Assistant</span>
                                <Badge variant="secondary" className="text-[10px] badge-gradient">Online</Badge>
                              </div>
                              <div className="p-3 rounded-2xl rounded-tl-sm bg-muted text-sm">
                                Hi! How can I help you today?
                              </div>
                            </div>
                          </motion.div>
                          {/* User Message */}
                          <motion.div
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 1.3 }}
                            className="flex items-start gap-3 flex-row-reverse"
                          >
                            <div className="w-10 h-10 rounded-full bg-muted flex items-center justify-center shrink-0">
                              <Users className="h-5 w-5 text-muted-foreground" />
                            </div>
                            <div className="space-y-2 text-right">
                              <span className="text-sm font-medium">You</span>
                              <div className="p-3 rounded-2xl rounded-tr-sm message-bubble-user text-sm">
                                I need help with my account
                              </div>
                            </div>
                          </motion.div>
                          {/* Typing indicator */}
                          <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 1.6 }}
                            className="flex items-start gap-3"
                          >
                            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white shrink-0 shadow-lg">
                              <Bot className="h-5 w-5" />
                            </div>
                            <div className="p-3 rounded-2xl rounded-tl-sm bg-muted">
                              <div className="typing-indicator">
                                <span></span>
                                <span></span>
                                <span></span>
                              </div>
                            </div>
                          </motion.div>
                        </div>
                        <div className="hidden md:block space-y-4">
                          <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 1.2 }}
                            className="stats-card flex items-center gap-4"
                          >
                            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-white shadow-lg">
                              <Zap className="h-6 w-6" />
                            </div>
                            <div>
                              <h3 className="font-semibold text-sm text-muted-foreground">Avg. Response Time</h3>
                              <p className="text-2xl font-bold font-display text-emerald-600 dark:text-emerald-400">1.2m</p>
                            </div>
                          </motion.div>
                          <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 1.4 }}
                            className="stats-card flex items-center gap-4"
                          >
                            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-400 to-indigo-500 flex items-center justify-center text-white shadow-lg">
                              <CheckCircle2 className="h-6 w-6" />
                            </div>
                            <div>
                              <h3 className="font-semibold text-sm text-muted-foreground">Resolution Rate</h3>
                              <p className="text-2xl font-bold font-display text-blue-600 dark:text-blue-400">99.8%</p>
                            </div>
                          </motion.div>
                        </div>
                      </div>
                    </div>
                  </div>
                </ScaleOnHover>

                {/* Decorative elements */}
                <div className="absolute -top-6 -right-6 w-32 h-32 bg-gradient-to-br from-primary/30 to-accent/30 rounded-full blur-3xl" />
                <div className="absolute -bottom-6 -left-6 w-40 h-40 bg-gradient-to-br from-accent/30 to-primary/30 rounded-full blur-3xl" />
              </div>
            </FadeIn>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-24 bg-muted/30 relative overflow-hidden">
        <div className="absolute inset-0 pattern-diagonal opacity-50" />
        <div className="container relative">
          <FadeInView direction="up" className="text-center max-w-2xl mx-auto mb-16">
            <Badge className="mb-4 badge-gradient">Features</Badge>
            <h2 className="font-display text-3xl md:text-4xl lg:text-5xl font-bold mb-4">
              Why Choose{" "}
              <span className="gradient-text">Our Support?</span>
            </h2>
            <p className="text-lg text-muted-foreground">
              We've built a platform that puts your needs first, combining technology and expertise.
            </p>
          </FadeInView>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
            {features.map((feature, index) => (
              <FadeInView key={feature.title} delay={feature.delay} direction="up">
                <Card className="feature-card group h-full bg-card/50 backdrop-blur-sm">
                  <CardContent className="pt-6">
                    <div className={`mb-6 w-14 h-14 rounded-2xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center text-white shadow-lg group-hover:scale-110 transition-all duration-300 group-hover:shadow-xl`}>
                      <feature.icon className="h-7 w-7" />
                    </div>
                    <h3 className="text-xl font-bold mb-3 font-display group-hover:gradient-text transition-all duration-300">
                      {feature.title}
                    </h3>
                    <p className="text-muted-foreground leading-relaxed">
                      {feature.description}
                    </p>
                  </CardContent>
                </Card>
              </FadeInView>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-24 relative overflow-hidden">
        <div className="container">
          <FadeInView direction="up" className="text-center max-w-2xl mx-auto mb-16">
            <Badge className="mb-4 badge-gradient">Testimonials</Badge>
            <h2 className="font-display text-3xl md:text-4xl lg:text-5xl font-bold mb-4">
              Loved by{" "}
              <span className="gradient-text">Thousands</span>
            </h2>
            <p className="text-lg text-muted-foreground">
              Don't just take our word for it. Here's what our customers say.
            </p>
          </FadeInView>

          <div className="grid md:grid-cols-3 gap-6 lg:gap-8">
            {testimonials.map((testimonial, index) => (
              <FadeInView key={testimonial.name} delay={index * 0.1} direction="up">
                <Card className="feature-card h-full bg-card/50 backdrop-blur-sm">
                  <CardContent className="pt-6">
                    <div className="flex gap-1 mb-4">
                      {[...Array(testimonial.rating)].map((_, i) => (
                        <Star key={i} className="h-5 w-5 fill-yellow-400 text-yellow-400" />
                      ))}
                    </div>
                    <p className="text-muted-foreground mb-6 leading-relaxed italic">
                      "{testimonial.content}"
                    </p>
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white font-bold">
                        {testimonial.name.charAt(0)}
                      </div>
                      <div>
                        <p className="font-semibold">{testimonial.name}</p>
                        <p className="text-sm text-muted-foreground">
                          {testimonial.role} at {testimonial.company}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </FadeInView>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 relative overflow-hidden">
        <div className="container relative z-10">
          <FadeInView direction="up">
            <div className="gradient-hero rounded-3xl p-8 md:p-16 text-center text-white overflow-hidden relative shadow-2xl">
              {/* Decorative elements */}
              <div className="absolute top-0 right-0 -mr-20 -mt-20 w-96 h-96 rounded-full bg-white/10 blur-3xl" />
              <div className="absolute bottom-0 left-0 -ml-20 -mb-20 w-80 h-80 rounded-full bg-black/10 blur-3xl" />
              <Float duration={4} distance={10} className="absolute top-10 left-10 w-20 h-20 rounded-full bg-white/5" />
              <Float duration={5} distance={15} className="absolute bottom-10 right-10 w-16 h-16 rounded-full bg-white/5" />

              <div className="relative z-10">
                <motion.div
                  initial={{ scale: 0.8, opacity: 0 }}
                  whileInView={{ scale: 1, opacity: 1 }}
                  transition={{ duration: 0.5 }}
                  viewport={{ once: true }}
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 backdrop-blur-sm text-sm font-medium mb-6"
                >
                  <Sparkles className="h-4 w-4" />
                  Get Started Today
                </motion.div>

                <h2 className="font-display text-3xl md:text-5xl font-bold mb-6">
                  Ready to Transform Your Support?
                </h2>
                <p className="text-blue-100 text-lg md:text-xl max-w-2xl mx-auto mb-10">
                  Join thousands of satisfied customers who experience the future of support today.
                </p>

                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <Link href="/support">
                    <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.98 }}>
                      <Button size="lg" variant="secondary" className="h-14 px-8 font-bold text-base shadow-xl hover:shadow-2xl transition-all">
                        Open a Ticket
                        <ArrowRight className="ml-2 h-5 w-5" />
                      </Button>
                    </motion.div>
                  </Link>
                  <Link href="/chat">
                    <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.98 }}>
                      <Button size="lg" className="h-14 px-8 bg-white/20 hover:bg-white/30 text-white border-white/20 backdrop-blur-sm font-bold text-base shadow-xl hover:shadow-2xl transition-all">
                        <MessageSquare className="mr-2 h-5 w-5" />
                        Chat Now
                      </Button>
                    </motion.div>
                  </Link>
                </div>
              </div>
            </div>
          </FadeInView>
        </div>
      </section>
    </div>
  )
}
