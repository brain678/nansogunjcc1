import { create } from "zustand"
import { persist } from "zustand/middleware"
import { User, AuthTokens } from "@/types"
import { tokenUtils, userUtils } from "@/lib/utils"

interface AuthState {
  user: User | null
  tokens: AuthTokens | null
  isLoading: boolean
  isAuthenticated: boolean
  hasHydrated: boolean

  // Actions
  setUser: (user: User) => void
  setTokens: (tokens: AuthTokens) => void
  setAuthData: (user: User, tokens: AuthTokens) => void
  clearAuth: () => void
  setLoading: (loading: boolean) => void
  setHydrated: (hydrated: boolean) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      tokens: null,
      isLoading: false,
      isAuthenticated: false,
      hasHydrated: false,

      setUser: (user) => {
        set({ user, isAuthenticated: !!user })
        if (user) {
          userUtils.setCurrentUser(user)
        }
      },

      setTokens: (tokens) => {
        set({ tokens })
        if (tokens) {
          tokenUtils.setTokens(tokens.accessToken, tokens.refreshToken)
        }
      },

      setAuthData: (user, tokens) => {
        set({
          user,
          tokens,
          isAuthenticated: true,
        })
        userUtils.setCurrentUser(user)
        tokenUtils.setTokens(tokens.accessToken, tokens.refreshToken)
      },

      clearAuth: () => {
        set({
          user: null,
          tokens: null,
          isAuthenticated: false,
        })
        userUtils.clearCurrentUser()
        tokenUtils.clearTokens()
      },

      setLoading: (loading) => {
        set({ isLoading: loading })
      },

      setHydrated: (hydrated) => {
        set({ hasHydrated: hydrated })
      },
    }),
    {
      name: "auth-storage",
      onRehydrateStorage: () => (state) => {
        // Called after rehydration
        if (state) {
          state.setHydrated(true)
        }
      },
    }
  )
)
