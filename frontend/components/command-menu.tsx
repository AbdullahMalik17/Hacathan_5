"use client"

import * as React from "react"
import { useRouter } from "next/navigation"
import {
  MessageSquare,
  FileText,
  Home,
  Search,
  Moon,
  Sun,
  Laptop,
  HelpCircle,
  Mail,
  Phone,
  ExternalLink,
  Sparkles,
} from "lucide-react"
import { useTheme } from "next-themes"

import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
  CommandShortcut,
} from "@/components/ui/command"

export function CommandMenu() {
  const [open, setOpen] = React.useState(false)
  const router = useRouter()
  const { setTheme, theme } = useTheme()

  React.useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        setOpen((open) => !open)
      }
      // Quick shortcuts
      if (e.key === "/" && !e.metaKey && !e.ctrlKey) {
        const target = e.target as HTMLElement
        if (
          target.tagName !== "INPUT" &&
          target.tagName !== "TEXTAREA" &&
          !target.isContentEditable
        ) {
          e.preventDefault()
          setOpen(true)
        }
      }
    }

    document.addEventListener("keydown", down)
    return () => document.removeEventListener("keydown", down)
  }, [])

  const runCommand = React.useCallback((command: () => void) => {
    setOpen(false)
    command()
  }, [])

  return (
    <CommandDialog open={open} onOpenChange={setOpen}>
      <CommandInput placeholder="Type a command or search..." />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>

        <CommandGroup heading="Navigation">
          <CommandItem
            onSelect={() => runCommand(() => router.push("/"))}
            className="gap-2"
          >
            <Home className="h-4 w-4" />
            <span>Home</span>
            <CommandShortcut>G H</CommandShortcut>
          </CommandItem>
          <CommandItem
            onSelect={() => runCommand(() => router.push("/chat"))}
            className="gap-2"
          >
            <MessageSquare className="h-4 w-4" />
            <span>Live Chat</span>
            <CommandShortcut>G C</CommandShortcut>
          </CommandItem>
          <CommandItem
            onSelect={() => runCommand(() => router.push("/support"))}
            className="gap-2"
          >
            <FileText className="h-4 w-4" />
            <span>Submit Ticket</span>
            <CommandShortcut>G S</CommandShortcut>
          </CommandItem>
        </CommandGroup>

        <CommandSeparator />

        <CommandGroup heading="Quick Actions">
          <CommandItem
            onSelect={() => runCommand(() => router.push("/chat"))}
            className="gap-2"
          >
            <Sparkles className="h-4 w-4" />
            <span>Start AI Conversation</span>
          </CommandItem>
          <CommandItem
            onSelect={() =>
              runCommand(() => window.open("mailto:support@company.com"))
            }
            className="gap-2"
          >
            <Mail className="h-4 w-4" />
            <span>Send Email</span>
          </CommandItem>
          <CommandItem
            onSelect={() => runCommand(() => window.open("tel:+15551234567"))}
            className="gap-2"
          >
            <Phone className="h-4 w-4" />
            <span>Call Support</span>
          </CommandItem>
        </CommandGroup>

        <CommandSeparator />

        <CommandGroup heading="Theme">
          <CommandItem
            onSelect={() => runCommand(() => setTheme("light"))}
            className="gap-2"
          >
            <Sun className="h-4 w-4" />
            <span>Light Mode</span>
            {theme === "light" && <span className="ml-auto text-xs">✓</span>}
          </CommandItem>
          <CommandItem
            onSelect={() => runCommand(() => setTheme("dark"))}
            className="gap-2"
          >
            <Moon className="h-4 w-4" />
            <span>Dark Mode</span>
            {theme === "dark" && <span className="ml-auto text-xs">✓</span>}
          </CommandItem>
          <CommandItem
            onSelect={() => runCommand(() => setTheme("system"))}
            className="gap-2"
          >
            <Laptop className="h-4 w-4" />
            <span>System Theme</span>
            {theme === "system" && <span className="ml-auto text-xs">✓</span>}
          </CommandItem>
        </CommandGroup>

        <CommandSeparator />

        <CommandGroup heading="Help">
          <CommandItem
            onSelect={() => runCommand(() => router.push("/support"))}
            className="gap-2"
          >
            <HelpCircle className="h-4 w-4" />
            <span>FAQ</span>
          </CommandItem>
        </CommandGroup>
      </CommandList>

      <div className="border-t px-3 py-2">
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <div className="flex items-center gap-2">
            <kbd className="pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground">
              ↑↓
            </kbd>
            <span>Navigate</span>
          </div>
          <div className="flex items-center gap-2">
            <kbd className="pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground">
              ↵
            </kbd>
            <span>Select</span>
          </div>
          <div className="flex items-center gap-2">
            <kbd className="pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground">
              Esc
            </kbd>
            <span>Close</span>
          </div>
        </div>
      </div>
    </CommandDialog>
  )
}

// Search trigger button component
export function CommandMenuTrigger() {
  return (
    <button
      onClick={() => {
        const event = new KeyboardEvent("keydown", {
          key: "k",
          metaKey: true,
          bubbles: true,
        })
        document.dispatchEvent(event)
      }}
      className="inline-flex items-center gap-2 rounded-full bg-background/50 px-3 py-1.5 text-sm text-muted-foreground shadow-sm backdrop-blur-sm transition-colors hover:bg-accent hover:text-accent-foreground"
    >
      <Search className="h-4 w-4" />
      <span className="hidden md:inline">Search...</span>
      <kbd className="pointer-events-none hidden h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground md:inline-flex">
        <span className="text-xs">⌘</span>K
      </kbd>
    </button>
  )
}
