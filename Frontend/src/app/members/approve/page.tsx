import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { MemberApprovalQueue } from "@/features/members/components/member-approval-queue"

export const metadata = {
  title: "Approve Members - NANS Platform",
  description: "Review and approve member applications",
}

export default function ApproveApplicantsPage() {
  return (
    <DashboardLayout>
      <MemberApprovalQueue />
    </DashboardLayout>
  )
}
