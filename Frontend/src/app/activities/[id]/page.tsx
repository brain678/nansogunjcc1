import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { ActivityDetails } from "@/features/activities/components/activity-details"

export const metadata = {
  title: "Activity Details - NANS Platform",
  description: "View activity details and check in",
}

export default function ActivityDetailsPage() {
  return (
    <DashboardLayout>
      <ActivityDetails />
    </DashboardLayout>
  )
}
