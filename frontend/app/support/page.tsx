import { Metadata } from "next"
import { SupportForm } from "@/components/support-form"
import { Mail, MessageCircle, Globe, Clock, Zap, Shield, Sparkles } from "lucide-react"

export const metadata: Metadata = {
  title: "Contact Support",
  description:
    "Get help from our AI-powered support team. Available 24/7 via email, WhatsApp, or web form.",
}

const features = [
  {
    icon: Zap,
    title: "Instant AI Responses",
    description: "Our AI agent processes your request and responds within minutes.",
    color: "from-sky-500 to-blue-600",
    bgColor: "bg-sky-50",
    iconColor: "text-sky-600",
  },
  {
    icon: Clock,
    title: "24/7 Availability",
    description: "Support available round the clock, every day of the year.",
    color: "from-blue-500 to-indigo-500",
    bgColor: "bg-blue-50",
    iconColor: "text-blue-600",
  },
  {
    icon: Shield,
    title: "Secure & Private",
    description: "Your data is encrypted and handled with care.",
    color: "from-emerald-500 to-teal-500",
    bgColor: "bg-emerald-50",
    iconColor: "text-emerald-600",
  },
]

const channels = [
  {
    icon: Mail,
    title: "Email",
    description: "support@company.com",
    responseTime: "Within 5 minutes",
    gradient: "from-blue-500 to-indigo-500",
  },
  {
    icon: MessageCircle,
    title: "WhatsApp",
    description: "+1 (555) 123-4567",
    responseTime: "Within 2 minutes",
    gradient: "from-emerald-500 to-teal-500",
  },
  {
    icon: Globe,
    title: "Web Form",
    description: "Submit below",
    responseTime: "Within 5 minutes",
    gradient: "from-purple-500 to-pink-500",
  },
]

export default function SupportPage() {
  return (
    <div className="min-h-[calc(100vh-4rem)]">
      {/* Hero Section with animated background */}
      <section className="relative overflow-hidden border-b">
        {/* Gradient background */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-background to-accent/5" />

        {/* Animated blobs - blue/purple/indigo tones */}
        <div className="absolute top-0 -left-40 h-80 w-80 rounded-full bg-indigo-400 opacity-20 blur-3xl animate-float" />
        <div className="absolute top-20 right-0 h-80 w-80 rounded-full bg-blue-400 opacity-20 blur-3xl animate-float" style={{ animationDelay: "2s" }} />
        <div className="absolute -bottom-20 left-1/2 h-80 w-80 rounded-full bg-violet-400 opacity-20 blur-3xl animate-float" style={{ animationDelay: "4s" }} />

        {/* Grid pattern */}
        <div className="absolute inset-0 pattern-grid" />

        <div className="container relative py-20 md:py-28">
          <div className="mx-auto max-w-3xl text-center">
            {/* Badge */}
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-4 py-1.5 text-sm font-medium text-primary">
              <Sparkles className="h-4 w-4" />
              AI-Powered Support
            </div>

            <h1 className="animate-fade-in font-display text-4xl font-bold tracking-tight md:text-5xl lg:text-6xl">
              <span className="bg-gradient-to-r from-foreground via-foreground to-foreground/70 bg-clip-text text-transparent">
                How can we
              </span>
              <br />
              <span className="bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent">
                help you today?
              </span>
            </h1>

            <p className="mt-6 animate-fade-in text-lg text-muted-foreground md:text-xl" style={{ animationDelay: "0.1s" }}>
              Our AI-powered support team is available 24/7 to assist you with
              any questions or issues. Get instant, accurate responses.
            </p>
          </div>

          {/* Feature cards */}
          <div className="mt-16 grid gap-6 md:grid-cols-3">
            {features.map((feature, index) => (
              <div
                key={feature.title}
                className="animate-slide-up group relative rounded-2xl border bg-card p-6 shadow-sm transition-all duration-300 hover:shadow-xl hover:-translate-y-1"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                {/* Gradient border on hover */}
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-r opacity-0 transition-opacity group-hover:opacity-100 -z-10 blur-xl"
                  style={{ background: `linear-gradient(135deg, var(--tw-gradient-stops))` }}
                />

                <div className={`mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl ${feature.bgColor}`}>
                  <feature.icon className={`h-6 w-6 ${feature.iconColor}`} />
                </div>
                <h3 className="font-display text-lg font-semibold">{feature.title}</h3>
                <p className="mt-2 text-sm text-muted-foreground">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Main Content */}
      <section className="py-16 md:py-20">
        <div className="container">
          <div className="grid gap-12 lg:grid-cols-3">
            {/* Support Form */}
            <div className="lg:col-span-2">
              <SupportForm />
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Contact Channels */}
              <div className="rounded-2xl border bg-card p-6 shadow-sm">
                <h3 className="font-display text-lg font-semibold">
                  Other Ways to Reach Us
                </h3>
                <div className="mt-6 space-y-4">
                  {channels.map((channel) => (
                    <div key={channel.title} className="group flex gap-4 rounded-xl p-3 transition-colors hover:bg-muted/50">
                      <div className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br ${channel.gradient} shadow-lg shadow-primary/10`}>
                        <channel.icon className="h-5 w-5 text-white" />
                      </div>
                      <div>
                        <p className="font-semibold">{channel.title}</p>
                        <p className="text-sm text-muted-foreground">
                          {channel.description}
                        </p>
                        <p className="mt-1 text-xs font-medium text-accent">
                          {channel.responseTime}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* FAQ Preview */}
              <div className="rounded-2xl border bg-card p-6 shadow-sm">
                <h3 className="font-display text-lg font-semibold">
                  Common Questions
                </h3>
                <div className="mt-4 space-y-3">
                  <details className="group rounded-lg border border-transparent p-3 transition-colors hover:border-border hover:bg-muted/30">
                    <summary className="cursor-pointer text-sm font-medium text-foreground hover:text-primary transition-colors">
                      What are your response times?
                    </summary>
                    <p className="mt-3 text-sm text-muted-foreground leading-relaxed">
                      Our AI agent typically responds within 2-5 minutes for all
                      channels. High-priority requests are handled first.
                    </p>
                  </details>
                  <details className="group rounded-lg border border-transparent p-3 transition-colors hover:border-border hover:bg-muted/30">
                    <summary className="cursor-pointer text-sm font-medium text-foreground hover:text-primary transition-colors">
                      Can I track my support ticket?
                    </summary>
                    <p className="mt-3 text-sm text-muted-foreground leading-relaxed">
                      Yes! After submitting, you'll receive a ticket ID that you
                      can use to track the status of your request.
                    </p>
                  </details>
                  <details className="group rounded-lg border border-transparent p-3 transition-colors hover:border-border hover:bg-muted/30">
                    <summary className="cursor-pointer text-sm font-medium text-foreground hover:text-primary transition-colors">
                      Will I talk to a human?
                    </summary>
                    <p className="mt-3 text-sm text-muted-foreground leading-relaxed">
                      Our AI handles most requests, but complex issues are
                      automatically escalated to our human support team.
                    </p>
                  </details>
                  <details className="group rounded-lg border border-transparent p-3 transition-colors hover:border-border hover:bg-muted/30">
                    <summary className="cursor-pointer text-sm font-medium text-foreground hover:text-primary transition-colors">
                      Is my data secure?
                    </summary>
                    <p className="mt-3 text-sm text-muted-foreground leading-relaxed">
                      Absolutely. All communications are encrypted, and we follow
                      strict data protection guidelines.
                    </p>
                  </details>
                </div>
              </div>

              {/* Status Indicator */}
              <div className="rounded-2xl border border-emerald-200 bg-gradient-to-br from-emerald-50 to-teal-50 p-6 shadow-sm">
                <div className="flex items-center gap-4">
                  <div className="relative">
                    <div className="h-4 w-4 rounded-full bg-emerald-500 shadow-lg shadow-emerald-500/50" />
                    <div className="absolute inset-0 h-4 w-4 animate-ping rounded-full bg-emerald-500 opacity-75" />
                  </div>
                  <div>
                    <p className="font-semibold text-emerald-900">All Systems Operational</p>
                    <p className="text-sm text-emerald-700">
                      Support is available 24/7
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
