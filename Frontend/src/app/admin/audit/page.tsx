import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { AuditLogs } from "@/features/admin/audit-logs"

export const metadata = {
  title: "Audit Logs - NANS Platform",
  description: "View system audit logs",
}

export default function AuditLogsPage() {
  return (
    <DashboardLayout>
      <AuditLogs />
    </DashboardLayout>
  )
}
