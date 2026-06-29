import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { ActivitiesList } from "@/features/activities/components/activities-list"

export const metadata = {
  title: "Activities - NANS Platform",
  description: "View and participate in activities",
}

export default function ActivitiesPage() {
  return (
    <DashboardLayout>
      <ActivitiesList />
    </DashboardLayout>
  )
}
