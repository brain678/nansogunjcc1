import { apiClient } from "@/lib/api-client"
import { API_ENDPOINTS } from "@/lib/config"
import { ProfileUpdateRequest, PasswordChangeRequest, ProfilePhotoResponse, User } from "@/types"

const normalizeUser = (user: any): User => ({
  ...user,
  firstName: user?.firstName ?? user?.first_name ?? "",
  lastName: user?.lastName ?? user?.last_name ?? "",
  profilePhotoUrl: user?.profilePhotoUrl ?? user?.profile_photo_url ?? undefined,
  membershipStatus: user?.membershipStatus ?? user?.membership_status ?? undefined,
  membershipNumber: user?.membershipNumber ?? user?.membership_number ?? undefined,
  membershipReviewComments: user?.membershipReviewComments ?? user?.membership_review_comments ?? undefined,
  membershipRejectedAt: user?.membershipRejectedAt ?? user?.membership_rejected_at ?? undefined,
  qrToken: user?.qrToken ?? user?.qr_token ?? undefined,
  createdAt: user?.createdAt ?? user?.created_at ?? "",
  updatedAt: user?.updatedAt ?? user?.updated_at ?? "",
  lastLoginAt: user?.lastLoginAt ?? user?.last_login_at ?? undefined,
  mfaEnabled: user?.mfaEnabled ?? user?.mfa_enabled ?? false,
  roles: user?.roles ?? [],
})

export const profileService = {
  async getProfile(): Promise<User> {
    const user = await apiClient.get<any>(API_ENDPOINTS.auth.me)
    return normalizeUser(user)
  },

  async updateProfile(data: ProfileUpdateRequest): Promise<User> {
    const user = await apiClient.put<any>(API_ENDPOINTS.auth.updateProfile, data)
    return normalizeUser(user)
  },

  async uploadProfilePhoto(file: File): Promise<ProfilePhotoResponse> {
    const formData = new FormData()
    formData.append("photo", file)

    return apiClient.post<ProfilePhotoResponse>(
      API_ENDPOINTS.auth.uploadProfilePhoto,
      formData
    )
  },

  async changePassword(data: PasswordChangeRequest): Promise<{ message: string }> {
    return apiClient.post<{ message: string }>(API_ENDPOINTS.auth.changePassword, data)
  },
}
