// User and Authentication Types
export enum UserRole {
  ADMIN = "admin",
  GENERAL_SECRETARY = "general_secretary",
  CHAIRMAN = "chairman",
  MEMBER = "member",
}

export enum MembershipStatus {
  ACTIVE = "active",
  INACTIVE = "inactive",
  SUSPENDED = "suspended",
  RESIGNED = "resigned",
  PENDING = "pending",
  REJECTED = "rejected",
}

export enum MembershipType {
  FULL = "full",
  ASSOCIATE = "associate",
  STUDENT = "student",
  HONORARY = "honorary",
}

export enum MembershipTier {
  STANDARD = "standard",
  PREMIUM = "premium",
  LIFETIME = "lifetime",
}

export interface AuditEntry {
  timestamp: string
  action: string
  performedByUserId?: string
  performedByRole?: string
  comment?: string
  resultingStatus: MembershipStatus
  metadata: Record<string, any>
}

export interface User {
  id: string
  email: string
  firstName: string
  lastName: string
  phone?: string
  profilePhotoUrl?: string
  roles: UserRole[]
  mfaEnabled: boolean
  status: "active" | "inactive" | "locked"
  membershipStatus?: MembershipStatus | string | null
  membershipNumber?: string | null
  membershipReviewComments?: string | null
  membershipRejectedAt?: string | null
  qrToken?: string | null
  lastLoginAt?: string
  createdAt: string
  updatedAt: string
}

export interface AuthTokens {
  accessToken: string
  refreshToken: string
  tokenType: string
  expiresIn: number
}

export interface CreateUserResponse {
  id: string
  email: string
  firstName: string
  lastName: string
  fullName: string
  status: string
  roles: UserRole[]
  primaryOrganizationId: string
  createdAt: string
}

export interface LoginResponse {
  user: User
  token: AuthTokens
}

export interface ProfileUpdateRequest {
  firstName?: string
  lastName?: string
  phone?: string
}

export interface ChangePasswordRequest {
  currentPassword: string
  newPassword: string
  newPasswordConfirm: string
}

export type PasswordChangeRequest = ChangePasswordRequest

export interface ProfilePhotoResponse {
  url: string
  filename?: string
  size?: number
  uploadedAt: string
}

export interface MessageResponse {
  message: string
}

export interface Member {
  id: string
  userId: string
  email: string
  firstName: string
  lastName: string
  fullName: string
  membershipNumber: string
  membershipType: MembershipType
  membershipTier: MembershipTier
  status: MembershipStatus
  joinedDate: string
  membershipExpiryDate?: string
  isMembershipExpired: boolean
  daysUntilExpiry?: number
  requestedExpiryMonths?: number
  dateOfBirth?: string
  submittedAt?: string
  approvedAt?: string
  rejectedAt?: string
  approverId?: string
  approverRole?: string
  reviewComments?: string
  address?: string
  notes?: string
  documentIds?: string[]
  
  auditLog?: AuditEntry[]
  membershipId?: string
  qrToken?: string
  cardStatus?: string
  bio?: string
  profilePhotoUrl?: string
  phone?: string
  organization?: string
  position?: string
  department?: string
  addresses?: Array<{
    street: string
    city: string
    state: string
    zipCode: string
    country: string
  }>
  emergencyContactName?: string
  emergencyContactPhone?: string
  newsletterSubscription?: boolean
  eventNotifications?: boolean
  communicationLanguage?: string
  lastActiveAt?: string
  meetingsAttended: number
  activitiesParticipated: number
  documentsContributed: number
  totalContributionHours: number
  createdAt: string
  updatedAt: string
}

export interface DigitalIdentity {
  id: string
  userId: string
  membershipId: string
  role: UserRole
  cardStatus: "active" | "disabled" | "expired"
  qrToken: string
  profileData: {
    firstName: string
    lastName: string
    email: string
    institution: string
    chapter: string
    profilePhotoUrl?: string
    createdDate: string
  }
  verificationCount: number
  lastVerifiedAt?: string
  cardExpiryDate?: string
  createdAt: string
  updatedAt: string
}

export interface Meeting {
  id: string
  title: string
  description?: string
  startDate: string
  endDate: string
  location: string
  organizer: string
  status: "scheduled" | "ongoing" | "completed" | "cancelled"
  agenda?: string
  notes?: string
  createdAt: string
  updatedAt: string
}

export interface Activity {
  id: string
  title: string
  description?: string
  startDate: string
  endDate: string
  location: string
  participants: number
  status: "scheduled" | "ongoing" | "completed" | "cancelled"
  createdAt: string
  updatedAt: string
}

export interface Document {
  id: string
  title: string
  description?: string
  fileUrl: string
  fileSize: number
  fileType: string
  category: string
  uploadedBy: string
  uploadedAt: string
  version: number
}

// Paginated Response
export interface PaginatedResponse<T> {
  total: number
  skip: number
  limit: number
  items: T[]
}

// API Error Response
export interface APIError {
  error: {
    message: string
    code: string
    statusCode: number
    details?: Record<string, any>
  }
}

// Notification Type
export interface Notification {
  id: string
  title: string
  message: string
  type: "success" | "error" | "warning" | "info"
  read: boolean
  createdAt: string
  actionUrl?: string
}
