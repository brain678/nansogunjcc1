"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"

export default function ErrorPage({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background to-muted p-4">
      <div className="text-center space-y-6">
        <div className="space-y-2">
          <h1 className="text-6xl font-bold">500</h1>
          <p className="text-2xl font-semibold text-muted-foreground">Server Error</p>
        </div>

        <p className="text-muted-foreground max-w-md">
          Something went wrong on our end. Please try again or contact support if the problem persists.
        </p>

        {process.env.NODE_ENV === "development" && error.message && (
          <div className="bg-destructive/10 rounded-md p-4 text-left text-sm">
            <p className="text-destructive font-mono">{error.message}</p>
          </div>
        )}

        <div className="flex gap-3 justify-center pt-4">
          <Button onClick={() => reset()}>Try Again</Button>
          <Link href="/dashboard">
            <Button variant="outline">Go to Dashboard</Button>
          </Link>
        </div>
      </div>
    </div>
  )
}
