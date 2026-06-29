import { AuthLayout } from "@/components/layout/auth-layout"
import { ResetPasswordForm } from "@/features/auth/components/reset-password-form"

export const metadata = {
  title: "Reset Password - NANS Platform",
  description: "Set a new password for your NANS account",
}

export default function ResetPasswordPage() {
  return (
    <AuthLayout>
      <ResetPasswordForm />
    </AuthLayout>
  )
}
