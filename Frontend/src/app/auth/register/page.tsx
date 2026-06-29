import { AuthLayout } from "@/components/layout/auth-layout"
import { RegisterForm } from "@/features/auth/components/register-form"

export const metadata = {
  title: "Create Account - NANS Platform",
  description: "Create a new NANS account",
}

export default function RegisterPage() {
  return (
    <AuthLayout>
      <RegisterForm />
    </AuthLayout>
  )
}
