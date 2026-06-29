"use client"

import React, { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/store/auth"
import { useCurrentUser } from "@/hooks/use-auth"
import { Logo } from "@/components/layout/logo"

export function AuthLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const { user, tokens, hasHydrated } = useAuthStore()
  const hasAuthToken = Boolean(tokens?.accessToken)
  const { data: currentUser, isLoading } = useCurrentUser({ enabled: hasHydrated && hasAuthToken })
  const effectiveUser = currentUser ?? user

  useEffect(() => {
    if (!hasHydrated || isLoading || !hasAuthToken) return

    if (effectiveUser) {
      router.replace("/dashboard")
    }
  }, [effectiveUser, hasHydrated, hasAuthToken, isLoading, router])

  if (!hasHydrated || isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="space-y-4 text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-primary/10">
            <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background to-muted p-4">
      <div className="w-full max-w-md space-y-8">
        <div className="flex items-center justify-center">
          <Logo className="gap-3" />
        </div>
        <div className="rounded-3xl border border-border bg-background p-8 shadow-sm">
          {children}
        </div>
      </div>
    </div>
  )
}
