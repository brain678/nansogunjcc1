import { AuthLayout } from "@/components/layout/auth-layout"
import { ForgotPasswordForm } from "@/features/auth/components/forgot-password-form"

export const metadata = {
  title: "Forgot Password - NANS Platform",
  description: "Reset your account password",
}

export default function ForgotPasswordPage() {
  return (
    <AuthLayout>
      <ForgotPasswordForm />
    </AuthLayout>
  )
}
