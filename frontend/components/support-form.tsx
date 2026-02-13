import { useState, useEffect } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { toast } from "sonner"
import { Loader2, Send, CheckCircle2, Copy, ArrowRight, ArrowLeft, User, Mail, MessageSquare, AlertCircle, Sparkles, BookOpen, ExternalLink } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"

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
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import { Confetti } from "@/components/confetti"

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

const mockKnowledgeBase = [
  { keywords: ["reset", "password", "login"], title: "How to reset your password", link: "#" },
  { keywords: ["billing", "invoice", "payment"], title: "Understanding your invoice", link: "#" },
  { keywords: ["track", "order", "status"], title: "Track your order status", link: "#" },
  { keywords: ["cancel", "refund", "return"], title: "Refund policy & returns", link: "#" },
]

export function SupportForm() {
  const [step, setStep] = useState(1)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitSuccess, setSubmitSuccess] = useState(false)
  const [ticketId, setTicketId] = useState<string | null>(null)
  const [suggestions, setSuggestions] = useState<{ title: string; link: string }[]>([])
  const [showConfetti, setShowConfetti] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setValue,
    watch,
    trigger,
  } = useForm<SupportFormData>({
    resolver: zodResolver(supportFormSchema),
    defaultValues: {
      priority: "normal",
    },
  })

  const formData = watch()
  const progress = (step / 3) * 100

  // Smart Suggestion Logic
  useEffect(() => {
    if (step === 2) {
      const text = `${formData.subject || ""} ${formData.message || ""}`.toLowerCase()
      if (text.length > 5) {
        const found = mockKnowledgeBase.filter(item => 
          item.keywords.some(keyword => text.includes(keyword))
        )
        setSuggestions(found)
      } else {
        setSuggestions([])
      }
    }
  }, [formData.subject, formData.message, step])

  const nextStep = async () => {
    let fieldsToValidate: (keyof SupportFormData)[] = []
    if (step === 1) fieldsToValidate = ["name", "email"]
    if (step === 2) fieldsToValidate = ["subject", "message"]

    const isValid = await trigger(fieldsToValidate)
    if (isValid) setStep((s) => s + 1)
  }

  const prevStep = () => setStep((s) => s - 1)

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
        setShowConfetti(true)
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
      setShowConfetti(true)
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
      <Card className="animate-fade-in border-emerald-200 bg-emerald-50/50 overflow-hidden relative glass-morphism shadow-2xl ring-1 ring-emerald-500/20">
        {showConfetti && <Confetti />}
        <div className="absolute top-0 left-0 w-full h-1 bg-emerald-500" />
        <CardContent className="pt-10">
          <div className="text-center">
            <motion.div 
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 260, damping: 20 }}
              className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-emerald-100 shadow-inner"
            >
              <CheckCircle2 className="h-10 w-10 text-emerald-600" />
            </motion.div>

            <h2 className="font-display text-3xl font-bold text-emerald-900">
              Request Submitted!
            </h2>

            <p className="mt-2 text-emerald-700 max-w-sm mx-auto">
              Your support request has been received and is being processed by our AI systems.
            </p>

            <div className="mt-8 rounded-2xl border border-emerald-200 bg-white p-6 shadow-sm">
              <p className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Your Ticket ID</p>
              <div className="mt-2 flex items-center justify-center gap-3">
                <code className="font-mono text-2xl font-bold text-primary px-3 py-1 bg-primary/5 rounded">
                  {ticketId}
                </code>
                <Button
                  variant="outline"
                  size="icon"
                  onClick={copyTicketId}
                  className="h-10 w-10 rounded-xl"
                  aria-label="Copy ticket ID"
                >
                  <Copy className="h-4 w-4" />
                </Button>
              </div>
              <p className="mt-3 text-xs text-muted-foreground">
                Save this ID for tracking your request in real-time
              </p>
            </div>

            <div className="mt-8 grid grid-cols-2 gap-4">
              <div className="p-4 rounded-xl bg-white border border-emerald-100 text-left">
                <p className="text-xs font-semibold text-emerald-800 uppercase">Confirmation</p>
                <p className="text-sm text-emerald-600 mt-1">Email sent in 30s</p>
              </div>
              <div className="p-4 rounded-xl bg-white border border-emerald-100 text-left">
                <p className="text-xs font-semibold text-emerald-800 uppercase">Resolution</p>
                <p className="text-sm text-emerald-600 mt-1">Expected in 5m</p>
              </div>
            </div>

            <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-center">
              <Button
                variant="ghost"
                className="rounded-full"
                onClick={() => {
                  setSubmitSuccess(false)
                  setTicketId(null)
                  setStep(1)
                }}
              >
                Submit New Request
              </Button>
              <Button asChild className="rounded-full btn-gradient px-8">
                <a href={`/ticket/${ticketId}`}>
                  Track Progress
                  <ArrowRight className="ml-2 h-4 w-4" />
                </a>
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="card-hover overflow-hidden border-none shadow-2xl glass-card">
      <div className="h-2 w-full bg-muted">
        <motion.div 
          className="h-full bg-gradient-to-r from-primary to-accent"
          initial={{ width: "0%" }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.5 }}
        />
      </div>
      
      <CardHeader className="pb-4">
        <div className="flex justify-between items-center mb-2">
          <Badge variant="secondary" className="rounded-full px-3 py-1 bg-primary/10 text-primary border-none">
            Step {step} of 3
          </Badge>
          <div className="flex gap-1">
            {[1, 2, 3].map((s) => (
              <div 
                key={s} 
                className={cn(
                  "h-1.5 w-6 rounded-full transition-colors duration-300",
                  s <= step ? "bg-primary" : "bg-muted"
                )} 
              />
            ))}
          </div>
        </div>
        <CardTitle className="font-display text-2xl">
          {step === 1 && "About You"}
          {step === 2 && "The Details"}
          {step === 3 && "Almost Done"}
        </CardTitle>
        <CardDescription>
          {step === 1 && "Start with your contact information."}
          {step === 2 && "Tell us what's happening."}
          {step === 3 && "Finalize your priority and submit."}
        </CardDescription>
      </CardHeader>

      <CardContent className="pt-0">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <AnimatePresence mode="wait">
            <motion.div
              key={step}
              initial={{ x: 20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: -20, opacity: 0 }}
              transition={{ duration: 0.3, ease: "easeInOut" }}
              className="space-y-5"
            >
              {step === 1 && (
                <>
                  <div className="space-y-2">
                    <Label htmlFor="name" className="flex items-center gap-2">
                      <User className="h-4 w-4 text-primary" /> Name
                    </Label>
                    <Input
                      {...register("name")}
                      id="name"
                      placeholder="Your full name"
                      className={cn("rounded-xl transition-all duration-300", errors.name && "border-destructive")}
                    />
                    {errors.name && <p className="text-xs text-destructive">{errors.name.message}</p>}
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email" className="flex items-center gap-2">
                      <Mail className="h-4 w-4 text-primary" /> Email
                    </Label>
                    <Input
                      {...register("email")}
                      type="email"
                      id="email"
                      placeholder="your.email@example.com"
                      className={cn("rounded-xl transition-all duration-300", errors.email && "border-destructive")}
                    />
                    {errors.email && <p className="text-xs text-destructive">{errors.email.message}</p>}
                  </div>
                </>
              )}

              {step === 2 && (
                <>
                  <div className="space-y-2">
                    <Label htmlFor="subject" className="flex items-center gap-2">
                      <AlertCircle className="h-4 w-4 text-primary" /> Subject
                    </Label>
                    <Input
                      {...register("subject")}
                      id="subject"
                      placeholder="Brief description of your issue"
                      className={cn("rounded-xl transition-all duration-300", errors.subject && "border-destructive")}
                    />
                    {errors.subject && <p className="text-xs text-destructive">{errors.subject.message}</p>}
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="message" className="flex items-center gap-2">
                      <MessageSquare className="h-4 w-4 text-primary" /> Message
                    </Label>
                    <Textarea
                      {...register("message")}
                      id="message"
                      rows={5}
                      placeholder="Please describe your issue in detail..."
                      className={cn("rounded-xl transition-all duration-300 min-h-[120px]", errors.message && "border-destructive")}
                    />
                    {errors.message && <p className="text-xs text-destructive">{errors.message.message}</p>}
                  </div>

                  <AnimatePresence>
                    {suggestions.length > 0 && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        exit={{ opacity: 0, height: 0 }}
                        className="rounded-xl border border-blue-200 bg-blue-50/50 p-4 space-y-3 overflow-hidden"
                      >
                        <div className="flex items-center gap-2 text-blue-700 font-semibold text-sm">
                          <Sparkles className="h-4 w-4" />
                          AI Suggestions
                        </div>
                        <div className="grid gap-2">
                          {suggestions.map((suggestion, idx) => (
                            <a 
                              key={idx} 
                              href={suggestion.link}
                              className="flex items-center justify-between p-3 rounded-lg bg-white/60 hover:bg-white transition-colors text-sm group"
                              onClick={(e) => e.preventDefault()} // Prevent nav for demo
                            >
                              <div className="flex items-center gap-2 text-muted-foreground group-hover:text-primary">
                                <BookOpen className="h-4 w-4" />
                                {suggestion.title}
                              </div>
                              <ExternalLink className="h-3 w-3 opacity-50 group-hover:opacity-100" />
                            </a>
                          ))}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </>
              )}

              {step === 3 && (
                <>
                  <div className="space-y-2">
                    <Label htmlFor="priority">Support Urgency</Label>
                    <Select
                      value={formData.priority}
                      onValueChange={(value: "normal" | "high") => setValue("priority", value)}
                    >
                      <SelectTrigger id="priority" className="rounded-xl h-12">
                        <SelectValue placeholder="Select priority" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="normal">Normal - Resolution in 10m</SelectItem>
                        <SelectItem value="high">High - Resolution in 5m</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="p-4 rounded-xl bg-primary/5 border border-primary/10 space-y-3">
                    <h4 className="text-sm font-semibold flex items-center gap-2">
                      <CheckCircle2 className="h-4 w-4 text-primary" /> Summary
                    </h4>
                    <div className="text-sm space-y-1 text-muted-foreground">
                      <p><span className="font-medium text-foreground">Name:</span> {formData.name}</p>
                      <p><span className="font-medium text-foreground">Subject:</span> {formData.subject}</p>
                    </div>
                  </div>
                </>
              )}
            </motion.div>
          </AnimatePresence>

          <div className="flex gap-3 pt-4">
            {step > 1 && (
              <Button
                type="button"
                variant="outline"
                onClick={prevStep}
                className="flex-1 rounded-xl h-12"
              >
                <ArrowLeft className="mr-2 h-4 w-4" /> Back
              </Button>
            )}
            
            {step < 3 ? (
              <Button
                type="button"
                onClick={nextStep}
                className="flex-[2] rounded-xl h-12 btn-gradient"
              >
                Continue <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            ) : (
              <Button
                type="submit"
                disabled={isSubmitting}
                className="flex-[2] rounded-xl h-12 btn-gradient"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Send className="mr-2 h-4 w-4" />
                    Submit Ticket
                  </>
                )}
              </Button>
            )}
          </div>
        </form>
      </CardContent>
    </Card>
  )
}
