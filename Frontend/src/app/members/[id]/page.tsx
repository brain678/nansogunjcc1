import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { MemberProfile } from "@/features/members/components/member-profile"

export const metadata = {
  title: "Member Profile - NANS Platform",
  description: "View member profile and details",
}

export default function MemberProfilePage() {
  return (
    <DashboardLayout>
      <MemberProfile />
    </DashboardLayout>
  )
}
