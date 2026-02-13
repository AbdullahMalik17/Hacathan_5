"use client"

import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { toast } from "sonner"
import { Loader2, Send, CheckCircle2, Copy, ArrowRight } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { cn } from "@/lib/utils"

// Validation schema (FR-035)
const supportFormSchema = z.object({
  name: z
    .string()
    .min(2, "Name must be at least 2 characters")
    .max(100, "Name must not exceed 100 characters"),
  email: z
    .string()
    .email("Please enter a valid email address")
    .min(5, "Email is required")
    .max(255, "Email must not exceed 255 characters"),
  subject: z
    .string()
    .min(5, "Subject must be at least 5 characters")
    .max(200, "Subject must not exceed 200 characters"),
  message: z
    .string()
    .min(10, "Message must be at least 10 characters")
    .max(5000, "Message must not exceed 5000 characters"),
  priority: z.enum(["normal", "high"]).default("normal"),
})

type SupportFormData = z.infer<typeof supportFormSchema>

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || ""

export function SupportForm() {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitSuccess, setSubmitSuccess] = useState(false)
  const [ticketId, setTicketId] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setValue,
    watch,
  } = useForm<SupportFormData>({
    resolver: zodResolver(supportFormSchema),
    defaultValues: {
      priority: "normal",
    },
  })

  const priority = watch("priority")

  const copyTicketId = () => {
    if (ticketId) {
      navigator.clipboard.writeText(ticketId)
      toast.success("Ticket ID copied to clipboard")
    }
  }

  const onSubmit = async (data: SupportFormData) => {
    setIsSubmitting(true)

    try {
      if (!API_BASE_URL) {
        // Demo mode - generate a mock ticket ID
        const mockTicketId = `DEMO-${Date.now().toString(36).toUpperCase()}`
        setTicketId(mockTicketId)
        setSubmitSuccess(true)
        reset()
        toast.success("Demo: Support request submitted!", {
          description: `Ticket ID: ${mockTicketId}`,
        })
        return
      }

      const response = await fetch(`${API_BASE_URL}/api/support/submit`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || "Failed to submit form")
      }

      const result = await response.json()

      setTicketId(result.ticket_id)
      setSubmitSuccess(true)
      reset()

      toast.success("Support request submitted successfully!", {
        description: `Ticket ID: ${result.ticket_id}`,
      })
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "An error occurred"
      toast.error("Failed to submit request", {
        description: errorMessage,
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  // Success state
  if (submitSuccess && ticketId) {
    return (
      <Card className="animate-fade-in border-emerald-200 bg-emerald-50/50">
        <CardContent className="pt-6">
          <div className="text-center">
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100">
              <CheckCircle2 className="h-8 w-8 text-emerald-600" />
            </div>

            <h2 className="font-display text-2xl font-bold text-emerald-900">
              Request Submitted!
            </h2>

            <p className="mt-2 text-emerald-700">
              Your support request has been received and is being processed.
            </p>

            <div className="mt-6 rounded-lg border border-emerald-200 bg-white p-4">
              <p className="text-sm text-muted-foreground">Your Ticket ID</p>
              <div className="mt-1 flex items-center justify-center gap-2">
                <code className="font-mono text-xl font-bold text-foreground">
                  {ticketId}
                </code>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={copyTicketId}
                  className="h-8 w-8"
                  aria-label="Copy ticket ID"
                >
                  <Copy className="h-4 w-4" />
                </Button>
              </div>
              <p className="mt-2 text-xs text-muted-foreground">
                Save this ID for tracking your request
              </p>
            </div>

            <div className="mt-6 space-y-2 text-sm text-emerald-700">
              <p>You will receive:</p>
              <ul className="space-y-1">
                <li>• A confirmation email within 30 seconds</li>
                <li>• A detailed response within 5 minutes</li>
              </ul>
            </div>

            <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:justify-center">
              <Button
                variant="outline"
                onClick={() => {
                  setSubmitSuccess(false)
                  setTicketId(null)
                }}
              >
                Submit Another Request
              </Button>
              <Button asChild>
                <a href={`/ticket/${ticketId}`}>
                  Track Your Ticket
                  <ArrowRight className="ml-2 h-4 w-4" />
                </a>
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  // Form state
  return (
    <Card className="card-hover">
      <CardHeader>
        <div className="accent-line mb-4" />
        <CardTitle className="font-display">Contact Support</CardTitle>
        <CardDescription>
          Fill out the form below and our AI-powered support team will respond
          within minutes.
        </CardDescription>
      </CardHeader>

      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Name Field */}
          <div className="space-y-2">
            <Label htmlFor="name">
              Name <span className="text-destructive">*</span>
            </Label>
            <Input
              {...register("name")}
              id="name"
              placeholder="Your full name"
              aria-describedby={errors.name ? "name-error" : undefined}
              className={cn(errors.name && "border-destructive")}
            />
            {errors.name && (
              <p id="name-error" className="text-sm text-destructive">
                {errors.name.message}
              </p>
            )}
          </div>

          {/* Email Field */}
          <div className="space-y-2">
            <Label htmlFor="email">
              Email <span className="text-destructive">*</span>
            </Label>
            <Input
              {...register("email")}
              type="email"
              id="email"
              placeholder="your.email@example.com"
              aria-describedby={errors.email ? "email-error" : undefined}
              className={cn(errors.email && "border-destructive")}
            />
            {errors.email && (
              <p id="email-error" className="text-sm text-destructive">
                {errors.email.message}
              </p>
            )}
          </div>

          {/* Subject Field */}
          <div className="space-y-2">
            <Label htmlFor="subject">
              Subject <span className="text-destructive">*</span>
            </Label>
            <Input
              {...register("subject")}
              id="subject"
              placeholder="Brief description of your issue"
              aria-describedby={errors.subject ? "subject-error" : undefined}
              className={cn(errors.subject && "border-destructive")}
            />
            {errors.subject && (
              <p id="subject-error" className="text-sm text-destructive">
                {errors.subject.message}
              </p>
            )}
          </div>

          {/* Message Field */}
          <div className="space-y-2">
            <Label htmlFor="message">
              Message <span className="text-destructive">*</span>
            </Label>
            <Textarea
              {...register("message")}
              id="message"
              rows={6}
              placeholder="Please describe your issue in detail..."
              aria-describedby={errors.message ? "message-error" : undefined}
              className={cn(errors.message && "border-destructive")}
            />
            {errors.message && (
              <p id="message-error" className="text-sm text-destructive">
                {errors.message.message}
              </p>
            )}
            <p className="text-xs text-muted-foreground">
              Minimum 10 characters, maximum 5000 characters
            </p>
          </div>

          {/* Priority Field */}
          <div className="space-y-2">
            <Label htmlFor="priority">Priority</Label>
            <Select
              value={priority}
              onValueChange={(value: "normal" | "high") =>
                setValue("priority", value)
              }
            >
              <SelectTrigger id="priority">
                <SelectValue placeholder="Select priority" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="normal">
                  Normal - Response within 10 minutes
                </SelectItem>
                <SelectItem value="high">
                  High - Response within 5 minutes
                </SelectItem>
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground">
              Select high priority for urgent issues
            </p>
          </div>

          {/* Submit Button */}
          <Button
            type="submit"
            disabled={isSubmitting}
            className="w-full"
            size="lg"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Submitting...
              </>
            ) : (
              <>
                <Send className="mr-2 h-4 w-4" />
                Submit Support Request
              </>
            )}
          </Button>
        </form>

        <div className="mt-6 border-t pt-6 text-center">
          <p className="text-sm text-muted-foreground">
            Need immediate assistance? Email us at{" "}
            <a
              href="mailto:support@company.com"
              className="font-medium text-primary hover:underline"
            >
              support@company.com
            </a>
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
