export const API_CONFIG = {
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  basePath: process.env.NEXT_PUBLIC_API_BASE_PATH || "/api/v1",
  timeout: 30000,
} as const

export const STORAGE_KEYS = {
  accessToken: `${process.env.NEXT_PUBLIC_STORAGE_KEY_PREFIX || "nans_"}access_token`,
  refreshToken: `${process.env.NEXT_PUBLIC_STORAGE_KEY_PREFIX || "nans_"}refresh_token`,
  user: `${process.env.NEXT_PUBLIC_STORAGE_KEY_PREFIX || "nans_"}user`,
  theme: `${process.env.NEXT_PUBLIC_STORAGE_KEY_PREFIX || "nans_"}theme`,
} as const

export const ROUTES = {
  // Auth
  login: "/auth/login",
  register: "/auth/register",
  forgotPassword: "/auth/forgot-password",
  resetPassword: "/auth/reset-password",
  logout: "/auth/logout",
  
  // Dashboard
  dashboard: "/dashboard",
  
  // Members
  members: "/members",
  memberProfile: "/members/:id",
  memberCreate: "/members/create",
  memberApprove: "/members/approve",
  
  // Meetings
  meetings: "/meetings",
  meetingDetail: "/meetings/:id",
  meetingCreate: "/meetings/create",
  
  // Activities
  activities: "/activities",
  activityDetail: "/activities/:id",
  activityCreate: "/activities/create",
  
  // Digital ID
  myIdCard: "/my-id-card",
  idCardDownload: "/my-id-card/download",
  
  // QR
  qrScanner: "/qr-scanner",
  qrVerify: "/qr-verify",
  
  // Documents
  documents: "/documents",
  documentsArchive: "/documents/archive",
  
  // Settings
  settings: "/settings",
  profile: "/profile",
  
  // Admin
  admin: "/admin",
  adminUsers: "/admin/users",
  adminAudit: "/admin/audit",
  
  // Error
  unauthorized: "/unauthorized",
  forbidden: "/forbidden",
  notFound: "/not-found",
  error: "/error",
} as const

export const API_ENDPOINTS = {
  // Auth
  auth: {
    login: "/auth/login",
    refresh: "/auth/refresh",
    me: "/auth/me",
    updateProfile: "/auth/me",
    changePassword: "/auth/change-password",
    uploadProfilePhoto: "/auth/me/photo",
    logout: "/auth/logout",
    register: "/auth/register",
    forgotPassword: "/auth/forgot-password",
    resetPassword: "/auth/reset-password",
  },
  
  // Members
  members: {
    list: "/members",
    pending: "/members/pending",
    get: "/members/:id",
    getByMembership: "/members/by-membership/:number",
    register: "/members/register",
    approve: "/members/:id/approve",
    reject: "/members/:id/reject",
    suspend: "/members/:id/suspend",
    reactivate: "/members/:id/reactivate",
    update: "/members/:id",
    updateProfile: "/members/:id/profile",
    renew: "/members/:id/renew",
    upgradeTier: "/members/:id/upgrade-tier",
    activate: "/members/:id/activate",
    deactivate: "/members/:id/deactivate",
    alumni: "/members/:id/alumni",
    activity: "/members/:id/activity",
    statistics: "/members/statistics/overview",
    expiring: "/members/expiring/list",
    delete: "/members/:id",
  },
  
  // Meetings
  meetings: {
    list: "/meetings",
    get: "/meetings/:id",
    create: "/meetings",
    update: "/meetings/:id",
    delete: "/meetings/:id",
    approve: "/meetings/:id/approve/:memberId",
    attendance: "/meetings/:id/attendance",
    minutes: "/meetings/:id/minutes",
  },
  
  // Activities
  activities: {
    list: "/activities",
    get: "/activities/:id",
    create: "/activities",
    update: "/activities/:id",
    delete: "/activities/:id",
    checkin: "/activities/:id/checkin",
    participants: "/activities/:id/participants",
  },
  
  // Identity & QR
  identity: {
    get: "/identity/me",
    generateQr: "/identity/qr/generate",
    verifyQr: "/identity/qr/verify",
    disableCard: "/identity/card/disable",
    activateCard: "/identity/card/activate",
  },
  
  // Documents
  documents: {
    list: "/documents",
    get: "/documents/:id",
    upload: "/documents/upload",
    delete: "/documents/:id",
    archive: "/documents/archive",
  },
  
  // Users (Admin)
  users: {
    list: "/users",
    get: "/users/:id",
    create: "/users",
    update: "/users/:id",
    delete: "/users/:id",
    roles: "/users/:id/roles",
  },
  
  // Audit
  audit: {
    list: "/audit/logs",
  },
} as const

export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  INTERNAL_SERVER_ERROR: 500,
} as const
