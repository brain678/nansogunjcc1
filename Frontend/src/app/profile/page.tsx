import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { UserProfile } from "@/features/profile/user-profile"

export const metadata = {
  title: "My Profile - NANS Platform",
  description: "Manage your profile settings",
}

export default function ProfilePage() {
  return (
    <DashboardLayout>
      <UserProfile />
    </DashboardLayout>
  )
}
