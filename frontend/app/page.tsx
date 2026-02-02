import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ArrowRight, MessageSquare, Zap, Shield, Clock, CheckCircle2, Bot, Users, Sparkles } from "lucide-react"
import Link from "next/link"

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen overflow-hidden">
      {/* Hero Section */}
      <section className="relative pt-20 pb-16 md:pt-32 md:pb-24 lg:pt-40 lg:pb-32 overflow-hidden">
        {/* Background Elements */}
        <div className="absolute top-0 left-0 w-full h-full overflow-hidden -z-10">
          <div className="absolute top-[-20%] right-[-10%] w-[600px] h-[600px] rounded-full bg-primary/10 blur-[100px] animate-pulse" />
          <div className="absolute bottom-[-10%] left-[-10%] w-[500px] h-[500px] rounded-full bg-indigo-500/5 blur-[100px] animate-pulse" style={{ animationDelay: '2s' }} />
          <div className="absolute top-[20%] left-[20%] w-[300px] h-[300px] rounded-full bg-blue-400/10 blur-[80px] animate-float" />
          <div className="absolute inset-0 pattern-grid opacity-30" />
        </div>

        <div className="container relative z-10">
          <div className="flex flex-col items-center text-center max-w-4xl mx-auto">
            <div className="animate-fade-in flex items-center gap-2 px-3 py-1 rounded-full bg-background/50 backdrop-blur-sm border border-primary/20 text-sm font-medium text-primary mb-8 shadow-sm">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-primary opacity-75"></span>
                <span className="relative inline-flex h-2 w-2 rounded-full bg-primary"></span>
              </span>
              Next-Gen Support System
            </div>
            
            <h1 className="animate-fade-in font-display text-5xl md:text-7xl font-bold tracking-tight mb-6 leading-[1.1]">
              Customer Support, <br />
              <span className="bg-gradient-to-r from-primary via-blue-600 to-sky-500 bg-clip-text text-transparent">Reimagined.</span>
            </h1>
            
            <p className="animate-slide-up text-xl text-muted-foreground mb-10 max-w-2xl leading-relaxed" style={{ animationDelay: '0.1s' }}>
              Experience the perfect blend of AI speed and human empathy. 
              Get instant answers, 24/7 availability, and seamless resolution for all your needs.
            </p>
            
            <div className="animate-slide-up flex flex-col sm:flex-row items-center gap-4 w-full justify-center" style={{ animationDelay: '0.2s' }}>
              <Link href="/chat">
                <Button size="lg" className="h-14 px-8 text-base rounded-full btn-gradient shadow-lg shadow-primary/20">
                  <MessageSquare className="mr-2 h-5 w-5" />
                  Start Live Chat
                </Button>
              </Link>
              <Link href="/support">
                <Button variant="outline" size="lg" className="h-14 px-8 text-base rounded-full border-2 hover:bg-muted/50 backdrop-blur-sm bg-background/50">
                  Submit Ticket
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
            </div>

            {/* Floating UI Elements Mockup */}
            <div className="relative mt-20 w-full max-w-4xl animate-slide-up" style={{ animationDelay: '0.4s' }}>
              <div className="relative rounded-2xl border border-white/20 bg-white/40 backdrop-blur-xl shadow-2xl p-2 md:p-4 dark:bg-black/40 dark:border-white/10">
                <div className="rounded-xl overflow-hidden bg-background border shadow-inner">
                  {/* Mock Interface Header */}
                  <div className="h-12 bg-muted/50 border-b flex items-center px-4 gap-2">
                    <div className="flex gap-1.5">
                      <div className="w-3 h-3 rounded-full bg-slate-300/80" />
                      <div className="w-3 h-3 rounded-full bg-slate-300/80" />
                      <div className="w-3 h-3 rounded-full bg-slate-300/80" />
                    </div>
                    <div className="mx-auto w-1/3 h-2 rounded-full bg-foreground/5" />
                  </div>
                  {/* Mock Content */}
                  <div className="p-6 md:p-12 grid md:grid-cols-2 gap-8 items-center">
                    <div className="space-y-6">
                      <div className="flex items-start gap-4">
                        <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary shrink-0">
                          <Bot className="h-5 w-5" />
                        </div>
                        <div className="space-y-2">
                          <div className="h-4 w-24 bg-foreground/10 rounded" />
                          <div className="h-20 w-full bg-foreground/5 rounded-lg" />
                        </div>
                      </div>
                       <div className="flex items-start gap-4 flex-row-reverse">
                        <div className="w-10 h-10 rounded-full bg-accent/10 flex items-center justify-center text-accent shrink-0">
                          <Users className="h-5 w-5" />
                        </div>
                        <div className="space-y-2 text-right w-full">
                          <div className="h-4 w-24 bg-foreground/10 rounded ml-auto" />
                          <div className="h-12 w-3/4 bg-primary/10 rounded-lg ml-auto" />
                        </div>
                      </div>
                    </div>
                    <div className="hidden md:block space-y-4">
                        <div className="p-4 rounded-xl bg-card border shadow-sm flex items-center gap-4">
                            <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center text-green-600">
                                <Zap className="h-6 w-6" />
                            </div>
                            <div>
                                <h3 className="font-semibold">Avg. Response Time</h3>
                                <p className="text-2xl font-bold font-display">1.2m</p>
                            </div>
                        </div>
                        <div className="p-4 rounded-xl bg-card border shadow-sm flex items-center gap-4">
                             <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center text-blue-600">
                                <CheckCircle2 className="h-6 w-6" />
                            </div>
                            <div>
                                <h3 className="font-semibold">Resolution Rate</h3>
                                <p className="text-2xl font-bold font-display">99.8%</p>
                            </div>
                        </div>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Decorative blobs behind mockup */}
              <div className="absolute -top-10 -right-10 w-40 h-40 bg-accent rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob" />
              <div className="absolute -bottom-10 -left-10 w-40 h-40 bg-primary rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000" />
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-20 bg-muted/30 border-t border-b border-border/50">
        <div className="container">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="font-display text-3xl md:text-4xl font-bold mb-4">Why Choose Our Support?</h2>
            <p className="text-muted-foreground">We've built a platform that puts your needs first, combining technology and expertise.</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <Card className="feature-card group hover:border-primary/50 transition-all bg-card/50 backdrop-blur-sm">
              <CardContent className="pt-6">
                <div className="mb-6 w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-blue-500/20 group-hover:scale-110 transition-transform duration-300">
                  <Bot className="h-7 w-7" />
                </div>
                <h3 className="text-xl font-bold mb-3 font-display">AI-Powered Intelligence</h3>
                <p className="text-muted-foreground leading-relaxed">
                  Our advanced AI understands context, sentiment, and technical details to provide accurate resolutions instantly.
                </p>
              </CardContent>
            </Card>

            <Card className="feature-card group hover:border-indigo-500/50 transition-all bg-card/50 backdrop-blur-sm">
              <CardContent className="pt-6">
                <div className="mb-6 w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white shadow-lg shadow-indigo-500/20 group-hover:scale-110 transition-transform duration-300">
                  <Clock className="h-7 w-7" />
                </div>
                <h3 className="text-xl font-bold mb-3 font-display">24/7 Availability</h3>
                <p className="text-muted-foreground leading-relaxed">
                  Support never sleeps. Whether it's 2 PM or 2 AM, our systems are awake and ready to assist you immediately.
                </p>
              </CardContent>
            </Card>

            <Card className="feature-card group hover:border-emerald-500/50 transition-all bg-card/50 backdrop-blur-sm">
              <CardContent className="pt-6">
                <div className="mb-6 w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-white shadow-lg shadow-emerald-500/20 group-hover:scale-110 transition-transform duration-300">
                  <Shield className="h-7 w-7" />
                </div>
                <h3 className="text-xl font-bold mb-3 font-display">Enterprise Security</h3>
                <p className="text-muted-foreground leading-relaxed">
                  Bank-grade encryption and strict privacy protocols ensure your sensitive data remains protected at all times.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 relative overflow-hidden">
        <div className="container relative z-10">
          <div className="bg-gradient-to-r from-primary to-indigo-600 rounded-3xl p-8 md:p-16 text-center text-white overflow-hidden relative shadow-2xl shadow-primary/25">
             {/* Decorative circles */}
            <div className="absolute top-0 right-0 -mr-20 -mt-20 w-96 h-96 rounded-full bg-white/10 blur-3xl" />
            <div className="absolute bottom-0 left-0 -ml-20 -mb-20 w-80 h-80 rounded-full bg-black/10 blur-3xl" />
            
            <h2 className="font-display text-3xl md:text-5xl font-bold mb-6 relative z-10">Ready to get started?</h2>
            <p className="text-blue-100 text-lg md:text-xl max-w-2xl mx-auto mb-10 relative z-10">
              Join thousands of satisfied customers who experience the future of support today.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center relative z-10">
              <Link href="/support">
                <Button size="lg" variant="secondary" className="h-14 px-8 text-primary font-bold text-base shadow-xl hover:scale-105 transition-transform">
                  Open a Ticket
                </Button>
              </Link>
              <Link href="/chat">
                <Button size="lg" className="h-14 px-8 bg-white/20 hover:bg-white/30 text-white border-white/20 backdrop-blur-sm font-bold text-base shadow-xl hover:scale-105 transition-transform">
                  Chat Now
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}