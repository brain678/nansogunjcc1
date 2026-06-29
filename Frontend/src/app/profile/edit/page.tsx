import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { EditProfilePage } from "@/features/profile/edit-profile-page"

export const metadata = {
  title: "Edit Profile - NANS Platform",
  description: "Update your profile details and account settings",
}

export default function ProfileEditPage() {
  return (
    <DashboardLayout>
      <EditProfilePage />
    </DashboardLayout>
  )
}
