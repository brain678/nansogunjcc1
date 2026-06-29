import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from "axios"
import { API_CONFIG, STORAGE_KEYS } from "@/lib/config"

export class APIClient {
  private client: AxiosInstance
  private isRefreshing = false
  private failedQueue: Array<{
    resolve: (value: any) => void
    reject: (reason?: any) => void
  }> = []

  constructor() {
    this.client = axios.create({
      baseURL: `${API_CONFIG.baseURL}${API_CONFIG.basePath}`,
      timeout: API_CONFIG.timeout,
    })

    // Request interceptor to attach auth token
    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        const token = this.getAccessToken()
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor to handle token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & {
          _retry?: boolean
        }

        if (error.response?.status === 401 && !originalRequest._retry) {
          if (this.isRefreshing) {
            return new Promise((resolve, reject) => {
              this.failedQueue.push({ resolve, reject })
            })
              .then((token) => {
                originalRequest.headers.Authorization = `Bearer ${token}`
                return this.client(originalRequest)
              })
              .catch((err) => Promise.reject(err))
          }

          originalRequest._retry = true
          this.isRefreshing = true

          try {
            const refreshToken = this.getRefreshToken()
            if (!refreshToken) {
              this.clearAuth()
              if (typeof window !== "undefined" && !window.location.pathname.startsWith("/auth")) {
                window.location.href = "/auth/login"
              }
              return Promise.reject(error)
            }

            const response = await this.client.post("/auth/refresh", {
              refreshToken: refreshToken,
            })

            const accessToken = response.data.accessToken ?? response.data.access_token
            const newRefreshToken = response.data.refreshToken ?? response.data.refresh_token
            if (!accessToken || !newRefreshToken) {
              throw new Error("Invalid refresh token response")
            }
            this.setTokens(accessToken, newRefreshToken)

            this.failedQueue.forEach(({ resolve }) => resolve(accessToken))
            this.failedQueue = []

            originalRequest.headers.Authorization = `Bearer ${accessToken}`
            return this.client(originalRequest)
          } catch (refreshError) {
            this.clearAuth()
            if (typeof window !== "undefined" && !window.location.pathname.startsWith("/auth")) {
              window.location.href = "/auth/login"
            }
            this.failedQueue = []
            return Promise.reject(refreshError)
          } finally {
            this.isRefreshing = false
          }
        }

        return Promise.reject(error)
      }
    )
  }

  private getAccessToken(): string | null {
    if (typeof window === "undefined") return null
    return localStorage.getItem(STORAGE_KEYS.accessToken)
  }

  private getRefreshToken(): string | null {
    if (typeof window === "undefined") return null
    return localStorage.getItem(STORAGE_KEYS.refreshToken)
  }

  private setTokens(accessToken: string, refreshToken: string): void {
    if (typeof window === "undefined") return
    localStorage.setItem(STORAGE_KEYS.accessToken, accessToken)
    localStorage.setItem(STORAGE_KEYS.refreshToken, refreshToken)
  }

  private clearAuth(): void {
    if (typeof window === "undefined") return
    localStorage.removeItem(STORAGE_KEYS.accessToken)
    localStorage.removeItem(STORAGE_KEYS.refreshToken)
    localStorage.removeItem(STORAGE_KEYS.user)
  }

  // Public methods
  async get<T>(url: string, config?: any): Promise<T> {
    const response = await this.client.get<T>(url, config)
    return response.data
  }

  async post<T>(url: string, data?: any, config?: any): Promise<T> {
    const response = await this.client.post<T>(url, data, config)
    return response.data
  }

  async put<T>(url: string, data?: any, config?: any): Promise<T> {
    const response = await this.client.put<T>(url, data, config)
    return response.data
  }

  async patch<T>(url: string, data?: any, config?: any): Promise<T> {
    const response = await this.client.patch<T>(url, data, config)
    return response.data
  }

  async delete<T>(url: string, config?: any): Promise<T> {
    const response = await this.client.delete<T>(url, config)
    return response.data
  }

  getClient(): AxiosInstance {
    return this.client
  }
}

export const apiClient = new APIClient()
