"use client"

import React, { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { useAuthStore } from "@/store/auth"
import { useProfile, useUpdateProfile, useChangePassword } from "@/hooks/use-profile"
import { API_CONFIG } from "@/lib/config"
import { errorUtils } from "@/lib/utils"

const profileSchema = z.object({
  firstName: z.string().min(2, "First name must be at least 2 characters"),
  lastName: z.string().min(2, "Last name must be at least 2 characters"),
  email: z.string().email("Enter a valid email address"),
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

type ProfileFormData = z.infer<typeof profileSchema>

type PasswordFormData = z.infer<typeof passwordSchema>

export function UserProfile() {
  const router = useRouter()
  const { user: storedUser } = useAuthStore((state) => ({ user: state.user }))
  const { data: user, isLoading: isProfileLoading } = useProfile()
  const updateProfileMutation = useUpdateProfile()
  const changePasswordMutation = useChangePassword()
  const [isEditing, setIsEditing] = useState(false)
  const [passwordOpen, setPasswordOpen] = useState(false)
  const [message, setMessage] = useState<string | null>(null)
  const [passwordMessage, setPasswordMessage] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      firstName: user?.firstName || storedUser?.firstName || "",
      lastName: user?.lastName || storedUser?.lastName || "",
      email: user?.email || storedUser?.email || "",
      phone: user?.phone || storedUser?.phone || "",
    },
  })

  const {
    register: registerPassword,
    handleSubmit: handlePasswordSubmit,
    formState: { errors: passwordErrors, isSubmitting: isChangingPassword },
    reset: resetPasswordForm,
  } = useForm<PasswordFormData>({
    resolver: zodResolver(passwordSchema),
    defaultValues: {
      currentPassword: "",
      newPassword: "",
      newPasswordConfirm: "",
    },
  })

  useEffect(() => {
    if (user) {
      reset({
        firstName: user.firstName,
        lastName: user.lastName,
        email: user.email,
        phone: user.phone || "",
      })
    }
  }, [user, reset])

  const onSubmit = async (data: ProfileFormData) => {
    setMessage(null)
    try {
      await updateProfileMutation.mutateAsync({
        firstName: data.firstName,
        lastName: data.lastName,
        phone: data.phone || undefined,
      })
      setMessage("Profile updated successfully.")
      setIsEditing(false)
    } catch (err) {
      setMessage(errorUtils.getErrorMessage(err))
    }
  }

  const onPasswordSubmit = async (data: PasswordFormData) => {
    setPasswordMessage(null)
    try {
      await changePasswordMutation.mutateAsync({
        currentPassword: data.currentPassword,
        newPassword: data.newPassword,
        newPasswordConfirm: data.newPasswordConfirm,
      })
      setPasswordMessage("Password changed successfully.")
      resetPasswordForm()
      setPasswordOpen(false)
    } catch (err) {
      setPasswordMessage(errorUtils.getErrorMessage(err))
    }
  }

  const handleResubmitApplication = async () => {
    if (!profileUser?.id) return
    router.push(`/members/create?mode=resubmit&memberId=${profileUser.id}`)
  }

  const profileUser = user ?? storedUser
  const profileName = [profileUser?.firstName, profileUser?.lastName].filter(Boolean).join(" ") || profileUser?.email || "Profile"
  const isRejectedMembership = String(profileUser?.membershipStatus ?? "").toLowerCase() === "rejected"
  const rejectionReason = profileUser?.membershipReviewComments || null
  const rejectionDate = profileUser?.membershipRejectedAt ? new Date(profileUser.membershipRejectedAt).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" }) : null

  const resolveMediaUrl = (value?: string | null) => {
    if (!value) return null
    if (/^https?:\/\//i.test(value)) return value
    if (value.startsWith("/")) return `${API_CONFIG.baseURL}${value}`
    return `${API_CONFIG.baseURL}/${value}`
  }

  const resolvedProfilePhotoUrl = resolveMediaUrl(profileUser?.profilePhotoUrl)
  const showQrCard = Boolean(profileUser?.qrToken)
  const qrCodeUrl = profileUser?.qrToken
    ? `https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=${encodeURIComponent(profileUser.qrToken)}`
    : null

  const renderValue = (value: unknown, fallback = "Not provided") => {
    if (value === undefined || value === null || value === "") return fallback
    if (typeof value === "boolean") return value ? "Yes" : "No"
    return String(value)
  }

  const renderDate = (value?: string) => {
    if (!value) return "Not available"
    try {
      return new Date(value).toLocaleDateString(undefined, {
        year: "numeric",
        month: "short",
        day: "numeric",
      })
    } catch {
      return value
    }
  }

  if (!profileUser && isProfileLoading) {
    return <div>Loading...</div>
  }

  if (!profileUser) {
    return <div>Unable to load profile information.</div>
  }

  return (
    <div className="space-y-8 max-w-5xl">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">My Profile</h1>
        <p className="text-muted-foreground mt-2">Manage your personal details, membership information, and security settings</p>
      </div>

      {message && (
        <div className="rounded-md border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800 dark:border-emerald-900/40 dark:bg-emerald-900/20 dark:text-emerald-200">
          {message}
        </div>
      )}

      {passwordMessage && (
        <div className="rounded-md border border-blue-200 bg-blue-50 p-3 text-sm text-blue-800 dark:border-blue-900/40 dark:bg-blue-900/20 dark:text-blue-200">
          {passwordMessage}
        </div>
      )}

      <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <Card>
          <CardHeader>
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <CardTitle>Profile Overview</CardTitle>
                <CardDescription>Your account snapshot and current membership state</CardDescription>
              </div>
              <Badge variant={profileUser.mfaEnabled ? "success" : "warning"}>
                {profileUser.mfaEnabled ? "2FA Enabled" : "2FA Disabled"}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-5">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
              {resolvedProfilePhotoUrl ? (
                <img
                  src={resolvedProfilePhotoUrl}
                  alt={`${profileName} profile`}
                  className="h-20 w-20 rounded-full border border-border object-cover"
                />
              ) : (
                <div className="flex h-20 w-20 items-center justify-center rounded-full border border-border bg-slate-100 text-lg font-semibold text-muted-foreground">
                  {profileName.charAt(0).toUpperCase()}
                </div>
              )}
              <div>
                <h2 className="text-xl font-semibold">{profileName}</h2>
                <p className="text-sm text-muted-foreground">{profileUser.email}</p>
                <div className="mt-3 flex flex-wrap gap-2">
                  <Badge variant="secondary">{renderValue(profileUser.membershipStatus, "No membership")}</Badge>
                  <Badge variant="outline">{renderValue(profileUser.membershipNumber, "No membership number")}</Badge>
                </div>
              </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-3">
              <div className="rounded-xl border border-border bg-muted/50 p-3">
                <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Account Status</p>
                <p className="mt-1 font-semibold capitalize">{renderValue(profileUser.status)}</p>
              </div>
              <div className="rounded-xl border border-border bg-muted/50 p-3">
                <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Last Login</p>
                <p className="mt-1 font-semibold">{renderDate(profileUser.lastLoginAt)}</p>
              </div>
              <div className="rounded-xl border border-border bg-muted/50 p-3">
                <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Member Since</p>
                <p className="mt-1 font-semibold">{renderDate(profileUser.createdAt)}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Security</CardTitle>
            <CardDescription>Update your password and authentication settings</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button
              variant="outline"
              className="w-full"
              onClick={() => setPasswordOpen((open) => !open)}
            >
              {passwordOpen ? "Hide Password Form" : "Change Password"}
            </Button>

            {passwordOpen && (
              <form onSubmit={handlePasswordSubmit(onPasswordSubmit)} className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Current Password</label>
                  <Input
                    type="password"
                    {...registerPassword("currentPassword")}
                    disabled={isChangingPassword}
                  />
                  {passwordErrors.currentPassword && (
                    <p className="text-xs text-destructive">{passwordErrors.currentPassword.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">New Password</label>
                  <Input
                    type="password"
                    {...registerPassword("newPassword")}
                    disabled={isChangingPassword}
                  />
                  {passwordErrors.newPassword && (
                    <p className="text-xs text-destructive">{passwordErrors.newPassword.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Confirm New Password</label>
                  <Input
                    type="password"
                    {...registerPassword("newPasswordConfirm")}
                    disabled={isChangingPassword}
                  />
                  {passwordErrors.newPasswordConfirm && (
                    <p className="text-xs text-destructive">{passwordErrors.newPasswordConfirm.message}</p>
                  )}
                </div>

                <div className="flex gap-2">
                  <Button type="submit" disabled={isChangingPassword}>
                    Save Password
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      setPasswordOpen(false)
                      resetPasswordForm()
                    }}
                  >
                    Cancel
                  </Button>
                </div>
              </form>
            )}

            <Button variant="outline" className="w-full">
              {profileUser.mfaEnabled ? "Disable" : "Enable"} Two-Factor Authentication
            </Button>
            <Button variant="destructive" className="w-full">
              Delete Account
            </Button>
          </CardContent>
        </Card>
      </div>

      {isRejectedMembership && (
        <Card className="border-amber-300 bg-amber-50/70">
          <CardHeader>
            <CardTitle className="text-amber-900">Application rejected</CardTitle>
            <CardDescription className="text-amber-800">Your application needs attention before it can be approved.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm text-amber-900">
            <div>
              <p className="font-semibold">Rejection reason</p>
              <p>{rejectionReason || "No reason was provided yet."}</p>
            </div>
            {rejectionDate ? (
              <div>
                <p className="font-semibold">Rejected on</p>
                <p>{rejectionDate}</p>
              </div>
            ) : null}
            <Button
              variant="outline"
              className="border-amber-700 text-amber-900 hover:bg-amber-100"
              onClick={handleResubmitApplication}
            >
              Resubmit application
            </Button>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Personal Information</CardTitle>
          <CardDescription>Update the details that appear on your account</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <label className="text-sm font-medium">First Name</label>
                <Input {...register("firstName")} disabled={!isEditing || isSubmitting} />
                {errors.firstName && (
                  <p className="text-xs text-destructive">{errors.firstName.message}</p>
                )}
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Last Name</label>
                <Input {...register("lastName")} disabled={!isEditing || isSubmitting} />
                {errors.lastName && (
                  <p className="text-xs text-destructive">{errors.lastName.message}</p>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Email</label>
              <Input type="email" {...register("email")} disabled={true} />
              <p className="text-xs text-muted-foreground">Email cannot be changed</p>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Phone</label>
              <Input
                type="tel"
                {...register("phone")}
                disabled={!isEditing || isSubmitting}
                placeholder="Optional"
              />
              {errors.phone && (
                <p className="text-xs text-destructive">{errors.phone.message}</p>
              )}
            </div>

            <div className="flex gap-2 pt-4">
              {!isEditing ? (
                <Button type="button" onClick={() => setIsEditing(true)}>
                  Edit Profile
                </Button>
              ) : (
                <>
                  <Button type="submit" disabled={isSubmitting || updateProfileMutation.isPending}>
                    Save Changes
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      setIsEditing(false)
                      reset()
                    }}
                  >
                    Cancel
                  </Button>
                </>
              )}
            </div>
          </form>
        </CardContent>
      </Card>

      {showQrCard && qrCodeUrl ? (
        <Card>
          <CardHeader>
            <CardTitle>Digital Membership QR</CardTitle>
            <CardDescription>Your QR code for quick verification at events</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">This QR code is linked to your membership and can be used for verification.</p>
              <p className="font-semibold">{renderValue(profileUser.membershipNumber, "No membership number")}</p>
            </div>
            <img src={qrCodeUrl} alt={`${profileName} QR code`} className="h-40 w-40 rounded-lg border bg-white p-2" />
          </CardContent>
        </Card>
      ) : null}

      <Card>
        <CardHeader>
          <CardTitle>Account & Membership Details</CardTitle>
          <CardDescription>Administrative details linked to your account</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-2">
          <div>
            <p className="text-sm text-muted-foreground">Account ID</p>
            <p className="font-semibold">{renderValue(profileUser.id)}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Membership Number</p>
            <p className="font-semibold">{renderValue(profileUser.membershipNumber)}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Membership Status</p>
            <p className="font-semibold">{renderValue(profileUser.membershipStatus)}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Roles</p>
            <div className="mt-1 flex flex-wrap gap-2">
              {profileUser.roles?.map((role) => (
                <Badge key={role} variant="secondary" className="capitalize">
                  {role}
                </Badge>
              ))}
            </div>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Created On</p>
            <p className="font-semibold">{renderDate(profileUser.createdAt)}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Last Updated</p>
            <p className="font-semibold">{renderDate(profileUser.updatedAt)}</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
