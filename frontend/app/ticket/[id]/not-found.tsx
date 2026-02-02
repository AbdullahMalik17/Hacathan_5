import Link from "next/link"
import { FileQuestion } from "lucide-react"
import { Button } from "@/components/ui/button"

export default function TicketNotFound() {
  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center">
      <div className="text-center">
        <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-muted">
          <FileQuestion className="h-10 w-10 text-muted-foreground" />
        </div>
        <h1 className="font-display text-3xl font-bold">Ticket Not Found</h1>
        <p className="mt-2 text-muted-foreground">
          We couldn't find a ticket with that ID. Please check the ID and try
          again.
        </p>
        <div className="mt-6 flex justify-center gap-3">
          <Button variant="outline" asChild>
            <Link href="/support">Submit New Request</Link>
          </Button>
          <Button asChild>
            <Link href="/">Go Home</Link>
          </Button>
        </div>
      </div>
    </div>
  )
}
