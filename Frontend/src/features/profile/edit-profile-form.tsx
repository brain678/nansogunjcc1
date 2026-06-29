"use client"

import { useEffect } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { User, ProfileUpdateRequest } from "@/types"
import { UseMutationResult } from "@tanstack/react-query"

const editProfileSchema = z.object({
  firstName: z.string().min(2, "First name must be at least 2 characters"),
  lastName: z.string().min(2, "Last name must be at least 2 characters"),
  phone: z
    .string()
    .optional()
    .transform((value) => {
      if (typeof value === "string") {
        const trimmed = value.trim()
        return trimmed === "" ? undefined : trimmed
      }
      return value
    }),
})

type EditProfileFormValues = z.infer<typeof editProfileSchema>

interface EditProfileFormProps {
  user: User
  mutation: UseMutationResult<User, Error, ProfileUpdateRequest, unknown>
  onSuccess?: () => void
}

export function EditProfileForm({ user, mutation, onSuccess }: EditProfileFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<EditProfileFormValues>({
    resolver: zodResolver(editProfileSchema),
    defaultValues: {
      firstName: user.firstName,
      lastName: user.lastName,
      phone: user.phone || "",
    },
  })

  useEffect(() => {
    reset({
      firstName: user.firstName,
      lastName: user.lastName,
      phone: user.phone || "",
    })
  }, [user, reset])

  const onSubmit = async (data: EditProfileFormValues) => {
    await mutation.mutateAsync({
      firstName: data.firstName,
      lastName: data.lastName,
      phone: data.phone || undefined,
    })
    onSuccess?.()
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="firstName">First Name</Label>
          <Input id="firstName" {...register("firstName")} disabled={isSubmitting} />
          {errors.firstName && <p className="text-xs text-destructive">{errors.firstName.message}</p>}
        </div>
        <div>
          <Label htmlFor="lastName">Last Name</Label>
          <Input id="lastName" {...register("lastName")} disabled={isSubmitting} />
          {errors.lastName && <p className="text-xs text-destructive">{errors.lastName.message}</p>}
        </div>
      </div>

      <div>
        <Label htmlFor="phone">Phone</Label>
        <Input id="phone" {...register("phone")} disabled={isSubmitting} />
        {errors.phone && <p className="text-xs text-destructive">{errors.phone.message}</p>}
      </div>

      <Button type="submit" disabled={isSubmitting || mutation.isPending}>
        Save profile
      </Button>
    </form>
  )
}
