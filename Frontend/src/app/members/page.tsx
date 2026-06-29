import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { MembersList } from "@/features/members/components/members-list"

export const metadata = {
  title: "Members - NANS Platform",
  description: "Manage organization members",
}

export default function MembersPage() {
  return (
    <DashboardLayout>
      <MembersList />
    </DashboardLayout>
  )
}
