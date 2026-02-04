import type { Metadata } from "next"
import { Inter, Space_Grotesk } from "next/font/google"
import { Toaster } from "sonner"
import { ThemeProvider } from "@/components/theme-provider"
import { ThemeToggle } from "@/components/theme-toggle"
import { CommandMenu, CommandMenuTrigger } from "@/components/command-menu"
import { TooltipProvider } from "@/components/ui/tooltip"
import "./globals.css"

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
})

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-space-grotesk",
  display: "swap",
})

export const metadata: Metadata = {
  title: {
    default: "Customer Support | Digital FTE",
    template: "%s | Customer Support",
  },
  description:
    "AI-powered customer support available 24/7. Get instant help via email, WhatsApp, or web form.",
  keywords: ["customer support", "help desk", "AI support", "24/7 support"],
  authors: [{ name: "Customer Success Team" }],
  openGraph: {
    type: "website",
    locale: "en_US",
    siteName: "Customer Support Portal",
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${inter.variable} ${spaceGrotesk.variable}`} suppressHydrationWarning>
      <body className="min-h-screen bg-background font-sans antialiased">
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <TooltipProvider delayDuration={0}>
            <div className="relative flex min-h-screen flex-col">
              {/* Command Menu - Global keyboard shortcut Ctrl+K */}
              <CommandMenu />

              {/* Header with glass effect */}
              <header className="sticky top-0 z-50 w-full bg-background/80 backdrop-blur-xl supports-[backdrop-filter]:bg-background/60">
                <div className="container flex h-16 items-center justify-between">
                  <a href="/" className="flex items-center space-x-3 group">
                    <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-accent shadow-lg shadow-primary/25 transition-all duration-300 group-hover:scale-110 group-hover:shadow-xl group-hover:shadow-primary/30">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        className="h-5 w-5 text-white"
                      >
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                      </svg>
                      <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-accent to-primary opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        className="absolute h-5 w-5 text-white"
                      >
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                      </svg>
                    </div>
                    <div className="flex flex-col">
                      <span className="font-display text-xl font-bold gradient-text">
                        Support
                      </span>
                      <span className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider">
                        AI-Powered
                      </span>
                    </div>
                  </a>

                  <nav className="flex items-center space-x-1 md:space-x-2">
                    {/* Search trigger */}
                    <div className="hidden md:block">
                      <CommandMenuTrigger />
                    </div>

                    <a
                      href="/support"
                      className="hidden lg:inline-flex px-4 py-2 text-sm font-medium text-muted-foreground rounded-full transition-all duration-300 hover:text-foreground hover:bg-muted"
                    >
                      Contact Us
                    </a>
                    <a
                      href="/chat"
                      className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-primary to-accent px-4 py-2 md:px-5 md:py-2.5 text-sm font-semibold text-white shadow-lg shadow-primary/25 transition-all duration-300 hover:shadow-xl hover:shadow-primary/30 hover:scale-105 btn-glow"
                    >
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        className="h-4 w-4"
                      >
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                        <path d="M8 10h.01" />
                        <path d="M12 10h.01" />
                        <path d="M16 10h.01" />
                      </svg>
                      <span className="hidden sm:inline">Live Chat</span>
                    </a>

                    {/* Theme Toggle */}
                    <div className="ml-1">
                      <ThemeToggle />
                    </div>
                  </nav>
                </div>
              </header>

              {/* Main content */}
              <main className="flex-1">{children}</main>

              {/* Footer with gradient top border */}
              <footer className="relative bg-muted/30">
                <div className="container py-12">
                  <div className="grid gap-8 md:grid-cols-4">
                    <div className="md:col-span-2">
                      <div className="flex items-center space-x-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-accent shadow-lg shadow-primary/20">
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            className="h-5 w-5 text-white"
                          >
                            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                          </svg>
                        </div>
                        <span className="font-display text-xl font-bold">Customer Support</span>
                      </div>
                      <p className="mt-4 max-w-md text-sm text-muted-foreground leading-relaxed">
                        AI-powered support available 24/7. We combine cutting-edge artificial intelligence
                        with human expertise to ensure you get the help you need, when you need it.
                      </p>
                      <div className="mt-6 flex items-center gap-3">
                        <kbd className="hidden sm:inline-flex pointer-events-none h-7 select-none items-center gap-1 rounded-md border bg-muted px-2 font-mono text-[10px] font-medium text-muted-foreground">
                          <span className="text-xs">⌘</span>K
                        </kbd>
                        <span className="text-xs text-muted-foreground">Quick Search</span>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-semibold text-foreground">Contact Channels</h4>
                      <ul className="mt-4 space-y-3 text-sm text-muted-foreground">
                        <li className="flex items-center gap-2 group cursor-pointer">
                          <span className="h-1.5 w-1.5 rounded-full bg-primary transition-transform group-hover:scale-150" />
                          <span className="group-hover:text-foreground transition-colors">support@company.com</span>
                        </li>
                        <li className="flex items-center gap-2 group cursor-pointer">
                          <span className="h-1.5 w-1.5 rounded-full bg-accent transition-transform group-hover:scale-150" />
                          <span className="group-hover:text-foreground transition-colors">+1 (555) 123-4567</span>
                        </li>
                        <li className="flex items-center gap-2 group cursor-pointer">
                          <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 transition-transform group-hover:scale-150" />
                          <span className="group-hover:text-foreground transition-colors">Web Form 24/7</span>
                        </li>
                      </ul>
                    </div>

                    <div>
                      <h4 className="font-semibold text-foreground">Response Times</h4>
                      <ul className="mt-4 space-y-3 text-sm">
                        <li className="flex items-center justify-between">
                          <span className="text-muted-foreground">Email</span>
                          <span className="font-medium text-primary">5 min</span>
                        </li>
                        <li className="flex items-center justify-between">
                          <span className="text-muted-foreground">WhatsApp</span>
                          <span className="font-medium text-primary">2 min</span>
                        </li>
                        <li className="flex items-center justify-between">
                          <span className="text-muted-foreground">Live Chat</span>
                          <span className="font-medium gradient-text">Instant</span>
                        </li>
                      </ul>
                    </div>
                  </div>

                  <div className="mt-12 flex flex-col items-center justify-between gap-4 border-t border-border/50 pt-8 sm:flex-row">
                    <p className="text-sm text-muted-foreground">
                      &copy; {new Date().getFullYear()} Customer Support Portal. All rights reserved.
                    </p>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <span className="relative flex h-2 w-2">
                        <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
                        <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500" />
                      </span>
                      All systems operational
                    </div>
                  </div>
                </div>
              </footer>
            </div>
            <Toaster
              position="top-right"
              toastOptions={{
                style: {
                  background: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  color: "hsl(var(--card-foreground))",
                  boxShadow: "0 10px 40px -10px rgba(0,0,0,0.15)",
                },
              }}
            />
          </TooltipProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
