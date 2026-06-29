import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { AdminUserManagement } from "@/features/admin/user-management"

export const metadata = {
  title: "Admin Users - NANS Platform",
  description: "Manage administrator accounts",
}

export default function AdminUsersPage() {
  return (
    <DashboardLayout>
      <AdminUserManagement />
    </DashboardLayout>
  )
}
