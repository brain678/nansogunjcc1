"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useProfile, useUpdateProfile, useUploadPhoto, useChangePassword } from "@/hooks/use-profile"
import { EditProfileForm } from "@/features/profile/edit-profile-form"
import { UploadPhotoForm } from "@/features/profile/upload-photo-form"
import { ChangePasswordForm } from "@/features/profile/change-password-form"

export function EditProfilePage() {
  const { data: user, isLoading, error } = useProfile()
  const updateProfileMutation = useUpdateProfile()
  const uploadPhotoMutation = useUploadPhoto()
  const changePasswordMutation = useChangePassword()
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  if (isLoading) {
    return <div>Loading profile...</div>
  }

  if (error) {
    return <div>Unable to load profile. Please try again later.</div>
  }

  return (
    <div className="space-y-8 max-w-4xl">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Edit Profile</h1>
        <p className="text-muted-foreground mt-2">Update your personal details, photo, and password.</p>
      </div>

      {successMessage && (
        <div className="p-3 bg-green-50 text-green-800 rounded-md text-sm dark:bg-green-900/20 dark:text-green-200">
          {successMessage}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Personal Details</CardTitle>
        </CardHeader>
        <CardContent>
          <EditProfileForm
            user={user!}
            mutation={updateProfileMutation}
            onSuccess={() => setSuccessMessage("Profile updated successfully.")}
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Profile Photo</CardTitle>
        </CardHeader>
        <CardContent>
          <UploadPhotoForm
            mutation={uploadPhotoMutation}
            onSuccess={() => setSuccessMessage("Profile photo uploaded successfully.")}
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Security</CardTitle>
        </CardHeader>
        <CardContent>
          <ChangePasswordForm
            mutation={changePasswordMutation}
            onSuccess={() => setSuccessMessage("Password changed successfully.")}
          />
        </CardContent>
      </Card>
    </div>
  )
}
