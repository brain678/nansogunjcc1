import { STORAGE_KEYS } from "@/lib/config"
import { User } from "@/types"

// Token Management
export const tokenUtils = {
  getAccessToken: (): string | null => {
    if (typeof window === "undefined") return null
    return localStorage.getItem(STORAGE_KEYS.accessToken)
  },

  getRefreshToken: (): string | null => {
    if (typeof window === "undefined") return null
    return localStorage.getItem(STORAGE_KEYS.refreshToken)
  },

  setTokens: (accessToken: string, refreshToken: string): void => {
    if (typeof window === "undefined") return
    localStorage.setItem(STORAGE_KEYS.accessToken, accessToken)
    localStorage.setItem(STORAGE_KEYS.refreshToken, refreshToken)
  },

  clearTokens: (): void => {
    if (typeof window === "undefined") return
    localStorage.removeItem(STORAGE_KEYS.accessToken)
    localStorage.removeItem(STORAGE_KEYS.refreshToken)
  },

  isTokenExpired: (token: string): boolean => {
    try {
      const parts = token.split(".")
      if (parts.length !== 3) return true

      const decoded = JSON.parse(atob(parts[1]))
      const now = Date.now() / 1000

      return decoded.exp < now
    } catch {
      return true
    }
  },
}

// User Management
export const userUtils = {
  getCurrentUser: (): User | null => {
    if (typeof window === "undefined") return null
    const userStr = localStorage.getItem(STORAGE_KEYS.user)
    if (!userStr) return null
    try {
      return JSON.parse(userStr)
    } catch {
      return null
    }
  },

  setCurrentUser: (user: User): void => {
    if (typeof window === "undefined") return
    localStorage.setItem(STORAGE_KEYS.user, JSON.stringify(user))
  },

  clearCurrentUser: (): void => {
    if (typeof window === "undefined") return
    localStorage.removeItem(STORAGE_KEYS.user)
  },

  hasRole: (role: string): boolean => {
    const user = userUtils.getCurrentUser()
    if (!user) return false
    return user.roles.includes(role as any)
  },

  hasAnyRole: (roles: string[]): boolean => {
    const user = userUtils.getCurrentUser()
    if (!user) return false
    return roles.some((role) => user.roles.includes(role as any))
  },

  isAdmin: (): boolean => {
    return userUtils.hasRole("admin")
  },

  isGeneralSecretary: (): boolean => {
    return userUtils.hasRole("general_secretary")
  },

  isChairman: (): boolean => {
    return userUtils.hasRole("chairman")
  },

  isMember: (): boolean => {
    return userUtils.hasRole("member")
  },
}

// Date Formatting
export const dateUtils = {
  formatDate: (date: string | Date, format: string = "MMM dd, yyyy"): string => {
    const d = typeof date === "string" ? new Date(date) : date
    const options: Intl.DateTimeFormatOptions = {
      year: "numeric",
      month: format.includes("MMM") ? "short" : "2-digit",
      day: "2-digit",
    }
    return d.toLocaleDateString("en-US", options)
  },

  formatTime: (date: string | Date): string => {
    const d = typeof date === "string" ? new Date(date) : date
    return d.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
    })
  },

  formatDateTime: (date: string | Date): string => {
    const d = typeof date === "string" ? new Date(date) : date
    return d.toLocaleString("en-US", {
      year: "numeric",
      month: "short",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
    })
  },

  getDaysUntil: (date: string | Date): number => {
    const d = typeof date === "string" ? new Date(date) : date
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    d.setHours(0, 0, 0, 0)
    const diff = d.getTime() - today.getTime()
    return Math.ceil(diff / (1000 * 60 * 60 * 24))
  },
}

// String Formatting
export const stringUtils = {
  capitalize: (str: string): string => {
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase()
  },

  toTitleCase: (str: string): string => {
    return str
      .split(" ")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(" ")
  },

  truncate: (str: string, length: number = 50): string => {
    if (str.length <= length) return str
    return str.slice(0, length) + "..."
  },

  toCamelCase: (str: string): string => {
    return str
      .toLowerCase()
      .replace(/[^a-zA-Z0-9]+(.)/g, (_, char) => char.toUpperCase())
  },

  toKebabCase: (str: string): string => {
    return str
      .toLowerCase()
      .replace(/\s+/g, "-")
      .replace(/[^\w-]/g, "")
  },
}

// Number Formatting
export const numberUtils = {
  formatCurrency: (
    amount: number,
    currency: string = "USD",
    locale: string = "en-US"
  ): string => {
    return new Intl.NumberFormat(locale, {
      style: "currency",
      currency,
    }).format(amount)
  },

  formatNumber: (num: number, decimals: number = 0): string => {
    return num.toLocaleString("en-US", {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    })
  },

  abbreviateNumber: (num: number): string => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + "M"
    if (num >= 1000) return (num / 1000).toFixed(1) + "K"
    return num.toString()
  },
}

// Validation
export const validationUtils = {
  isEmail: (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  },

  isPhoneNumber: (phone: string): boolean => {
    const phoneRegex = /^[\d\s\-\+\(\)]+$/
    return phoneRegex.test(phone) && phone.replace(/\D/g, "").length >= 10
  },

  isStrongPassword: (password: string): boolean => {
    return (
      password.length >= 8 &&
      /[a-z]/.test(password) &&
      /[A-Z]/.test(password) &&
      /[0-9]/.test(password) &&
      /[!@#$%^&*]/.test(password)
    )
  },

  isMembershipNumber: (number: string): boolean => {
    const membershipRegex = /^[A-Z]{2,4}-\d{4}-\d{6}$/
    return membershipRegex.test(number)
  },
}

// Error Handling
export const errorUtils = {
  getErrorMessage: (error: any): string => {
    if (typeof error === "string") return error
    if (error?.response?.data?.error?.message) {
      return error.response.data.error.message
    }
    if (error?.message) return error.message
    return "An unexpected error occurred"
  },

  isNetworkError: (error: any): boolean => {
    return error?.code === "ERR_NETWORK" || error?.response?.status === 0
  },

  isUnauthorized: (error: any): boolean => {
    return error?.response?.status === 401
  },

  isForbidden: (error: any): boolean => {
    return error?.response?.status === 403
  },

  isNotFound: (error: any): boolean => {
    return error?.response?.status === 404
  },
}

// Array/Object Utilities
export const collectionUtils = {
  groupBy: <T, K extends PropertyKey>(
    arr: T[],
    key: (item: T) => K
  ): Record<K, T[]> => {
    return arr.reduce(
      (result, item) => {
        const groupKey = key(item)
        if (!result[groupKey]) {
          result[groupKey] = []
        }
        result[groupKey].push(item)
        return result
      },
      {} as Record<K, T[]>
    )
  },

  unique: <T>(arr: T[], key?: (item: T) => any): T[] => {
    if (!key) return [...new Set(arr)]
    const seen = new Set()
    return arr.filter((item) => {
      const k = key(item)
      if (seen.has(k)) return false
      seen.add(k)
      return true
    })
  },

  flatten: <T>(arr: T[][]): T[] => {
    return arr.reduce((acc, val) => acc.concat(val), [])
  },
}
