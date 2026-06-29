"use client"

import { useEffect } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { UseMutationResult } from "@tanstack/react-query"
import { PasswordChangeRequest } from "@/types"

const passwordSchema = z
  .object({
    currentPassword: z.string().min(1, "Current password is required"),
    newPassword: z
      .string()
      .min(8, "New password must be at least 8 characters")
      .regex(/[A-Z]/, "Must include an uppercase letter")
      .regex(/[a-z]/, "Must include a lowercase letter")
      .regex(/[0-9]/, "Must include a number")
      .regex(/[!@#$%^&*]/, "Must include a special character"),
    newPasswordConfirm: z.string().min(1, "Confirm your new password"),
  })
  .refine((data) => data.newPassword === data.newPasswordConfirm, {
    message: "Passwords must match",
    path: ["newPasswordConfirm"],
  })

type PasswordFormValues = z.infer<typeof passwordSchema>

interface ChangePasswordFormProps {
  mutation: UseMutationResult<{ message: string }, Error, PasswordChangeRequest, unknown>
  onSuccess?: () => void
}

export function ChangePasswordForm({ mutation, onSuccess }: ChangePasswordFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<PasswordFormValues>({
    resolver: zodResolver(passwordSchema),
    defaultValues: {
      currentPassword: "",
      newPassword: "",
      newPasswordConfirm: "",
    },
  })

  useEffect(() => {
    reset({
      currentPassword: "",
      newPassword: "",
      newPasswordConfirm: "",
    })
  }, [reset])

  const onSubmit = async (data: PasswordFormValues) => {
    await mutation.mutateAsync({
      currentPassword: data.currentPassword,
      newPassword: data.newPassword,
      newPasswordConfirm: data.newPasswordConfirm,
    })
    reset()
    onSuccess?.()
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <Label htmlFor="currentPassword">Current Password</Label>
        <Input id="currentPassword" type="password" {...register("currentPassword")} disabled={isSubmitting} />
        {errors.currentPassword && <p className="text-xs text-destructive">{errors.currentPassword.message}</p>}
      </div>

      <div>
        <Label htmlFor="newPassword">New Password</Label>
        <Input id="newPassword" type="password" {...register("newPassword")} disabled={isSubmitting} />
        {errors.newPassword && <p className="text-xs text-destructive">{errors.newPassword.message}</p>}
      </div>

      <div>
        <Label htmlFor="newPasswordConfirm">Confirm New Password</Label>
        <Input id="newPasswordConfirm" type="password" {...register("newPasswordConfirm")} disabled={isSubmitting} />
        {errors.newPasswordConfirm && <p className="text-xs text-destructive">{errors.newPasswordConfirm.message}</p>}
      </div>

      <Button type="submit" disabled={isSubmitting || mutation.isPending}>
        Change Password
      </Button>
    </form>
  )
}
