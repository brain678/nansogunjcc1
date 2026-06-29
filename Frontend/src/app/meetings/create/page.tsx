import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { CreateMeetingForm } from "@/features/meetings/components/create-meeting-form"

export const metadata = {
  title: "Create Meeting - NANS Platform",
  description: "Schedule a new meeting",
}

export default function CreateMeetingPage() {
  return (
    <DashboardLayout>
      <CreateMeetingForm />
    </DashboardLayout>
  )
}
