import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { CreateActivityForm } from "@/features/activities/components/create-activity-form"

export const metadata = {
  title: "Create Activity - NANS Platform",
  description: "Organize a new activity",
}

export default function CreateActivityPage() {
  return (
    <DashboardLayout>
      <CreateActivityForm />
    </DashboardLayout>
  )
}
