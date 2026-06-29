"use client"

import React, { useState } from "react"
import Link from "next/link"
import { useSearchParams } from "next/navigation"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useLogin } from "@/hooks/use-auth"

const loginSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(1, "Password is required"),
})

type LoginFormData = z.infer<typeof loginSchema>

export function LoginForm() {
  const searchParams = useSearchParams()
  const { mutate: login, isPending } = useLogin()
  const [error, setError] = useState<string | null>(null)

  const registered = searchParams?.get("registered") === "true"
  const resetSuccess = searchParams?.get("reset") === "success"

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  })

  const onSubmit = (data: LoginFormData) => {
    setError(null)
    login(data, {
      onError: (error: any) => {
        setError(error?.message || "Login failed. Please try again.")
      },
    })
  }

  return (
    <Card className="border-primary/10 bg-[#F5F7F5] shadow-sm">
      <CardHeader>
        <CardTitle className="text-[#008753]">Welcome Back</CardTitle>
        <CardDescription className="text-[#4B5F54]">Sign in to your NANS account</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {registered && (
            <div className="rounded-lg border border-[#008753]/20 bg-[#E8F7F1] p-4 text-sm text-[#006f45]">
              Your account has been created. Please sign in.
            </div>
          )}
          {resetSuccess && (
            <div className="rounded-lg border border-[#008753]/20 bg-[#E8F7F1] p-4 text-sm text-[#006f45]">
              Your password has been reset successfully. Please sign in.
            </div>
          )}
          {error && (
            <div className="rounded-md bg-[#FDECEC] p-3 text-sm text-[#B42318]">
              {error}
            </div>
          )}

          <div className="space-y-2">
            <label className="text-sm font-medium text-[#1E302A]">Email</label>
            <Input
              type="email"
              placeholder="Enter your email"
              {...register("email")}
              disabled={isPending}
            />
            {errors.email && (
              <p className="text-xs text-[#B42318]">{errors.email.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <label className="text-sm font-medium text-[#1E302A]">Password</label>
              <Link href="/auth/forgot-password" className="text-xs text-[#008753] hover:underline">
                Forgot password?
              </Link>
            </div>
            <Input
              type="password"
              placeholder="Enter your password"
              {...register("password")}
              disabled={isPending}
            />
            {errors.password && (
              <p className="text-xs text-[#B42318]">{errors.password.message}</p>
            )}
          </div>

          <Button type="submit" className="w-full" disabled={isPending}>
            {isPending ? "Signing in..." : "Sign In"}
          </Button>

          <p className="text-center text-sm text-[#4B5F54]">
            Don't have an account?{" "}
            <Link href="/auth/register" className="font-medium text-[#008753] hover:underline">
              Create account
            </Link>
          </p>
        </form>
      </CardContent>
    </Card>
  )
}
