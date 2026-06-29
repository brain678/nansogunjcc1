import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { MeetingsList } from "@/features/meetings/components/meetings-list"

export const metadata = {
  title: "Meetings - NANS Platform",
  description: "View and manage meetings",
}

export default function MeetingsPage() {
  return (
    <DashboardLayout>
      <MeetingsList />
    </DashboardLayout>
  )
}
