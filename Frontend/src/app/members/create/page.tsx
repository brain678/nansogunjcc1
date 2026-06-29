import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { CreateMemberForm } from "@/features/members/components/create-member-form"

export const metadata = {
  title: "Create Member - NANS Platform",
  description: "Register a new organization member",
}

export default function CreateMemberPage() {
  return (
    <DashboardLayout>
      <CreateMemberForm />
    </DashboardLayout>
  )
}
