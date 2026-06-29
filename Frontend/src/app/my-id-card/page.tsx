import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { DigitalIdCard } from "@/features/id-card/digital-id-card"

export const metadata = {
  title: "My ID Card - NANS Platform",
  description: "View your digital membership card",
}

export default function MyIdCardPage() {
  return (
    <DashboardLayout>
      <DigitalIdCard />
    </DashboardLayout>
  )
}
