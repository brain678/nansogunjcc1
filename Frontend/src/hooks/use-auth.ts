import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { authService } from "@/services/auth"
import { useAuthStore } from "@/store/auth"
import { useRouter } from "next/navigation"
import { errorUtils } from "@/lib/utils"

export const useLogin = () => {
  const router = useRouter()
  const { setAuthData } = useAuthStore()

  return useMutation({
    mutationFn: async (credentials: { email: string; password: string }) => {
      return authService.login(credentials.email, credentials.password)
    },
    onSuccess: (data) => {
      setAuthData(data.user, data.token)
      router.push("/dashboard")
    },
    onError: (error) => {
      console.error("Login failed:", errorUtils.getErrorMessage(error))
    },
  })
}

export const useRegister = () => {
  const router = useRouter()
  const { setAuthData } = useAuthStore()

  return useMutation({
    mutationFn: async (data: {
      email: string
      password: string
      firstName: string
      lastName: string
      phone?: string
      passportPhoto?: File
    }) => {
      const registeredUser = await authService.register({
        email: data.email,
        firstName: data.firstName,
        lastName: data.lastName,
        phone: data.phone,
        password: data.password,
      })

      try {
        const loginResp = await authService.login(data.email, data.password)
        const { user, token } = loginResp
        setAuthData(user, token)
      } catch (loginError) {
        console.warn("Auto-login after registration failed; continuing to membership form.", loginError)
      }

      return { success: true, user: registeredUser }
    },
    onSuccess: () => {
      router.push("/members/create")
    },
    onError: (error) => {
      console.error("Registration failed:", errorUtils.getErrorMessage(error))
    },
  })
}

export const useCurrentUser = (options?: { enabled?: boolean }) => {
  const { setUser, clearAuth } = useAuthStore()

  return useQuery({
    queryKey: ["auth", "me"],
    queryFn: async () => {
      try {
        const user = await authService.getCurrentUser()
        setUser(user)
        return user
      } catch (err) {
        clearAuth()
        throw err
      }
    },
    enabled: options?.enabled ?? true,
    retry: 1,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

export const useLogout = () => {
  const router = useRouter()
  const queryClient = useQueryClient()
  const { clearAuth } = useAuthStore()

  return useMutation({
    mutationFn: async () => {
      return authService.logout()
    },
    onSuccess: () => {
      clearAuth()
      queryClient.clear()
      router.push("/auth/login")
    },
    onError: (error) => {
      console.error("Logout failed:", errorUtils.getErrorMessage(error))
    },
  })
}

export const useForgotPassword = () => {
  return useMutation({
    mutationFn: async (email: string) => {
      return authService.forgotPassword(email)
    },
    onError: (error) => {
      console.error("Failed to send reset email:", errorUtils.getErrorMessage(error))
    },
  })
}

export const useResetPassword = () => {
  const router = useRouter()

  return useMutation({
    mutationFn: async (data: { token: string; newPassword: string }) => {
      return authService.resetPassword(data.token, data.newPassword)
    },
    onSuccess: () => {
      router.push("/auth/login?reset=success")
    },
    onError: (error) => {
      console.error("Password reset failed:", errorUtils.getErrorMessage(error))
    },
  })
}
