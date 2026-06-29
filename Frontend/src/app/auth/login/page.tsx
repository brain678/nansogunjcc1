import { AuthLayout } from "@/components/layout/auth-layout"
import { LoginForm } from "@/features/auth/components/login-form"

export const metadata = {
  title: "Sign In - NANS Platform",
  description: "Sign in to your NANS account",
}

export default function LoginPage() {
  return (
    <AuthLayout>
      <LoginForm />
    </AuthLayout>
  )
}
