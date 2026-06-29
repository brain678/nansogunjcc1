"use client"

import React from "react"
import { useAuthStore } from "@/store/auth"
import { userUtils } from "@/lib/utils"
import { AdminDashboard } from "@/features/dashboard/admin-dashboard"
import { GeneralSecretaryDashboard } from "@/features/dashboard/general-secretary-dashboard"
import { ChairmanDashboard } from "@/features/dashboard/chairman-dashboard"
import { MemberDashboard } from "@/features/dashboard/member-dashboard"

export function DashboardContent() {
  const user = useAuthStore((state) => state.user)

  if (!user) {
    return <div>Loading...</div>
  }

  if (userUtils.isAdmin()) {
    return <AdminDashboard />
  }

  if (userUtils.isGeneralSecretary()) {
    return <GeneralSecretaryDashboard />
  }

  if (userUtils.isChairman()) {
    return <ChairmanDashboard />
  }

  return <MemberDashboard />
}
