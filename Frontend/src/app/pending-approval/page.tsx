import { redirect } from "next/navigation"

export const metadata = {
  title: "Pending Approval - NANS Platform",
  description: "Your account is pending approval",
}

export default function PendingApprovalPage() {
  redirect("/dashboard")
}
