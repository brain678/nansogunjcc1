import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { DocumentsList } from "@/features/documents/components/documents-list"

export const metadata = {
  title: "Documents - NANS Platform",
  description: "Access organization documents",
}

export default function DocumentsPage() {
  return (
    <DashboardLayout>
      <DocumentsList />
    </DashboardLayout>
  )
}
