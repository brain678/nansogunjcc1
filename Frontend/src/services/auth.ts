import { apiClient } from "@/lib/api-client"
import { API_ENDPOINTS } from "@/lib/config"
import {
  LoginResponse,
  AuthTokens,
  CreateUserResponse,
  User,
  ProfileUpdateRequest,
  ChangePasswordRequest,
  MessageResponse,
} from "@/types"

type RegisterData = {
  firstName: string
  lastName: string
  phone?: string
  email: string
  password: string
  confirmPassword?: string
}

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

const normalizeTokens = (tokens: any): AuthTokens => ({
  accessToken: tokens?.accessToken ?? tokens?.access_token ?? "",
  refreshToken: tokens?.refreshToken ?? tokens?.refresh_token ?? "",
  tokenType: tokens?.tokenType ?? tokens?.token_type ?? "",
  expiresIn: tokens?.expiresIn ?? tokens?.expires_in ?? 0,
})

export const authService = {
  async login(email: string, password: string): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>(API_ENDPOINTS.auth.login, {
      email,
      password,
    })

    return {
      ...response,
      user: normalizeUser(response.user),
      token: normalizeTokens(response.token),
    }
  },

  async register(data: RegisterData): Promise<CreateUserResponse> {
    // Auth register expects a minimal JSON payload
    const payload = {
      email: data.email,
      firstName: data.firstName,
      lastName: data.lastName,
      phone: data.phone,
      password: data.password,
    }

    return apiClient.post<CreateUserResponse>(API_ENDPOINTS.auth.register, payload)
  },

  async uploadProfilePhoto(photo: File): Promise<{ url: string }> {
    const formData = new FormData()
    formData.append("photo", photo)
    return apiClient.post(API_ENDPOINTS.auth.uploadProfilePhoto, formData)
  },

  async getCurrentUser(): Promise<User> {
    const user = await apiClient.get<User>(API_ENDPOINTS.auth.me)
    return normalizeUser(user)
  },

  async updateProfile(data: ProfileUpdateRequest): Promise<User> {
    return apiClient.put<User>(API_ENDPOINTS.auth.updateProfile, data)
  },

  async changePassword(data: ChangePasswordRequest): Promise<MessageResponse> {
    return apiClient.post<MessageResponse>(API_ENDPOINTS.auth.changePassword, data)
  },

  async refreshToken(refreshToken: string): Promise<AuthTokens> {
    return apiClient.post<AuthTokens>(API_ENDPOINTS.auth.refresh, {
      refreshToken: refreshToken,
    })
  },

  async logout(): Promise<void> {
    return apiClient.post(API_ENDPOINTS.auth.logout)
  },

  async forgotPassword(email: string): Promise<{ message: string }> {
    return apiClient.post(API_ENDPOINTS.auth.forgotPassword, { email })
  },

  async resetPassword(token: string, newPassword: string): Promise<{ message: string }> {
    return apiClient.post(API_ENDPOINTS.auth.resetPassword, {
      token,
      new_password: newPassword,
    })
  },
}
