import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { MeetingDetails } from "@/features/meetings/components/meeting-details"

export const metadata = {
  title: "Meeting Details - NANS Platform",
  description: "View meeting details and attendance",
}

export default function MeetingDetailsPage() {
  return (
    <DashboardLayout>
      <MeetingDetails />
    </DashboardLayout>
  )
}
