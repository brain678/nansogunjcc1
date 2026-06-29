"use client"

import React, { useEffect } from "react"
import { useRouter, usePathname } from "next/navigation"
import { Sidebar } from "@/components/layout/sidebar"
import { useAuthStore } from "@/store/auth"
import { useCurrentUser } from "@/hooks/use-auth"

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const pathname = usePathname()
  const { user, tokens, hasHydrated } = useAuthStore()
  const hasAuthToken = Boolean(tokens?.accessToken)
  const isCreateMemberRoute = pathname === "/members/create"
  const hasPendingMembershipData =
    typeof window !== "undefined" && Boolean(window.localStorage.getItem("pendingMembershipData"))
  const { data: currentUser, isLoading } = useCurrentUser({
    enabled: hasHydrated && hasAuthToken,
  })
  const effectiveUser = currentUser ?? user

  const membershipStatus = String(effectiveUser?.membershipStatus ?? "").toLowerCase()
  const isPendingMembership = membershipStatus === "pending"
  const isSuspendedMembership = membershipStatus === "suspended"
  const shouldBypassAuthGate = isCreateMemberRoute && (hasPendingMembershipData || hasAuthToken || Boolean(user))

  useEffect(() => {
    if (!hasHydrated) return

    if (shouldBypassAuthGate) return

    if (!effectiveUser && !isLoading) {
      router.replace("/auth/login")
    }
  }, [effectiveUser, hasHydrated, isLoading, router, shouldBypassAuthGate])

  if (!hasHydrated || isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#F5F7F5]">
        <div className="space-y-4 text-center">
          <div className="inline-flex h-12 w-12 items-center justify-center rounded-full bg-[#E8F7F1]">
            <div className="h-6 w-6 animate-spin rounded-full border-2 border-[#008753] border-t-transparent" />
          </div>
          <p className="text-[#4B5F54]">Loading...</p>
        </div>
      </div>
    )
  }

  if (!effectiveUser && hasHydrated) {
    return null
  }

  return (
    <div className="flex h-screen">
      <Sidebar />
      <main className="flex-1 overflow-auto md:ml-64">
        <div className="p-6">
          {isPendingMembership ? (
            <div className="mb-6 rounded-xl border border-[#008753]/20 bg-[#E8F7F1] p-4 text-sm text-[#006f45]">
              <p className="font-semibold">Membership pending approval</p>
              <p className="mt-1">You are signed in successfully, but your membership is still awaiting approval. You can continue using the dashboard while review is in progress.</p>
            </div>
          ) : null}
          {isSuspendedMembership ? (
            <div className="mb-6 rounded-xl border border-[#D62828]/30 bg-[#FDECEC] p-4 text-sm text-[#B42318]">
              <p className="font-semibold">Membership suspended</p>
              <p className="mt-1">Your membership has been suspended. Please contact the administration for assistance.</p>
            </div>
          ) : null}
          {children}
        </div>
      </main>
    </div>
  )
}
