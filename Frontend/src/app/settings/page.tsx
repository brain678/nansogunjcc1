import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { SettingsContent } from "@/features/settings/settings-content"

export const metadata = {
  title: "Settings - NANS Platform",
  description: "Manage your preferences",
}

export default function SettingsPage() {
  return (
    <DashboardLayout>
      <SettingsContent />
    </DashboardLayout>
  )
}

