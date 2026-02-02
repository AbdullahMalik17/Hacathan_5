import type { Metadata } from "next"
import { Inter, Space_Grotesk } from "next/font/google"
import { Toaster } from "sonner"
import { ThemeProvider } from "@/components/theme-provider"
import { ThemeToggle } from "@/components/theme-toggle"
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
          <div className="relative flex min-h-screen flex-col">
            {/* Header with gradient border */}
            <header className="sticky top-0 z-50 w-full border-b border-border/50 bg-background/80 backdrop-blur-xl">
              <div className="container flex h-16 items-center justify-between">
                <a href="/" className="flex items-center space-x-3 group">
                  <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-accent shadow-lg shadow-primary/25 transition-transform group-hover:scale-105">
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
                  <div>
                    <span className="font-display text-xl font-bold bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
                      Support
                    </span>
                    <span className="ml-2 text-xs font-medium text-accent">AI-Powered</span>
                  </div>
                </a>

                <nav className="flex items-center space-x-2">
                  <a
                    href="/support"
                    className="hidden md:inline-flex px-4 py-2 text-sm font-medium text-muted-foreground rounded-lg transition-colors hover:text-foreground hover:bg-muted"
                  >
                    Contact Us
                  </a>
                  <a
                    href="/chat"
                    className="hidden md:inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-primary to-accent px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-primary/25 transition-all hover:shadow-xl hover:shadow-accent/30 hover:scale-105"
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
                    Live Chat
                  </a>
                  
                  {/* Theme Toggle */}
                  <div className="ml-2">
                    <ThemeToggle />
                  </div>
                </nav>
              </div>
            </header>

            {/* Main content */}
            <main className="flex-1">{children}</main>

            {/* Footer with gradient top border */}
            <footer className="relative border-t bg-muted/30">
              <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-primary/50 to-transparent" />
              <div className="container py-12">
                <div className="grid gap-8 md:grid-cols-4">
                  <div className="md:col-span-2">
                    <div className="flex items-center space-x-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-accent">
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
                    <p className="mt-4 max-w-md text-sm text-muted-foreground">
                      AI-powered support available 24/7. We combine cutting-edge artificial intelligence
                      with human expertise to ensure you get the help you need, when you need it.
                    </p>
                  </div>

                  <div>
                    <h4 className="font-semibold text-foreground">Contact Channels</h4>
                    <ul className="mt-4 space-y-3 text-sm text-muted-foreground">
                      <li className="flex items-center gap-2">
                        <span className="h-1.5 w-1.5 rounded-full bg-accent" />
                        support@company.com
                      </li>
                      <li className="flex items-center gap-2">
                        <span className="h-1.5 w-1.5 rounded-full bg-accent" />
                        +1 (555) 123-4567
                      </li>
                      <li className="flex items-center gap-2">
                        <span className="h-1.5 w-1.5 rounded-full bg-accent" />
                        Web Form 24/7
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
                        <span className="font-medium text-accent">Instant</span>
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
        </ThemeProvider>
      </body>
    </html>
  )
}
