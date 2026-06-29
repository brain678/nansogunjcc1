import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { DashboardContent } from "@/features/dashboard/dashboard-content"

export const metadata = {
  title: "Dashboard - NANS Platform",
  description: "Your personal dashboard",
}

export default function DashboardPage() {
  return (
    <DashboardLayout>
      <DashboardContent />
    </DashboardLayout>
  )
}
