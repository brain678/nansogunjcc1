import { apiClient } from "@/lib/api-client"
import { API_ENDPOINTS } from "@/lib/config"
import { Member, PaginatedResponse } from "@/types"

const normalizeMember = (member: any): Member => ({
  ...member,
  firstName: member?.firstName ?? member?.first_name ?? "",
  lastName: member?.lastName ?? member?.last_name ?? "",
  fullName: member?.fullName ?? member?.full_name ?? "",
  profilePhotoUrl: member?.profilePhotoUrl ?? member?.profile_photo_url ?? undefined,
  membershipNumber: member?.membershipNumber ?? member?.membership_number ?? undefined,
  membershipType: member?.membershipType ?? member?.membership_type ?? "full",
  membershipTier: member?.membershipTier ?? member?.membership_tier ?? "standard",
  status: member?.status ?? member?.membership_status ?? "pending",
  joinedDate: member?.joinedDate ?? member?.joined_date ?? "",
  membershipExpiryDate: member?.membershipExpiryDate ?? member?.membership_expiry_date ?? undefined,
  submittedAt: member?.submittedAt ?? member?.submitted_at ?? undefined,
  approvedAt: member?.approvedAt ?? member?.approved_at ?? undefined,
  rejectedAt: member?.rejectedAt ?? member?.rejected_at ?? undefined,
  approverId: member?.approverId ?? member?.approver_id ?? undefined,
  approverRole: member?.approverRole ?? member?.approver_role ?? undefined,
  reviewComments: member?.reviewComments ?? member?.review_comments ?? undefined,
  documentIds: member?.documentIds ?? member?.document_ids ?? [],
  auditLog: member?.auditLog ?? member?.audit_log ?? [],
  membershipId: member?.membershipId ?? member?.membership_id ?? undefined,
  qrToken: member?.qrToken ?? member?.qr_token ?? undefined,
  cardStatus: member?.cardStatus ?? member?.card_status ?? undefined,
  bio: member?.bio ?? undefined,
  organization: member?.organization ?? undefined,
  position: member?.position ?? undefined,
  department: member?.department ?? undefined,
  emergencyContactName: member?.emergencyContactName ?? member?.emergency_contact_name ?? undefined,
  emergencyContactPhone: member?.emergencyContactPhone ?? member?.emergency_contact_phone ?? undefined,
  newsletterSubscription: member?.newsletterSubscription ?? member?.newsletter_subscription ?? undefined,
  eventNotifications: member?.eventNotifications ?? member?.event_notifications ?? undefined,
  communicationLanguage: member?.communicationLanguage ?? member?.communication_language ?? undefined,
  lastActiveAt: member?.lastActiveAt ?? member?.last_active_at ?? undefined,
  createdAt: member?.createdAt ?? member?.created_at ?? "",
  updatedAt: member?.updatedAt ?? member?.updated_at ?? "",
  dateOfBirth: member?.dateOfBirth ?? member?.date_of_birth ?? undefined,
})

const normalizeMemberStatistics = (stats: any) => ({
  totalMembers: stats?.total_members ?? 0,
  activeMembers: stats?.active_members ?? 0,
  inactiveMembers: stats?.inactive_members ?? 0,
  suspendedMembers: stats?.suspended_members ?? 0,
  membersByType: stats?.members_by_type ?? {},
  membersByTier: stats?.members_by_tier ?? {},
  totalContributionHours: stats?.total_contribution_hours ?? 0,
  averageMeetingsAttended: stats?.average_meetings_attended ?? 0,
})

type MembershipActionPayload = {
  comment?: string
}

type MemberResubmitPayload = {
  email: string
  firstName: string
  lastName: string
  phone?: string
  address?: string
  notes?: string
  dateOfBirth?: string
  membershipType?: string
  membershipTier?: string
  expiryMonths?: number
  comment?: string
}

export const memberService = {
  async register(data: {
    email: string
    firstName: string
    lastName: string
    phone?: string
    address?: string
    notes?: string
    membershipType?: string
    membershipTier?: string
    expiryMonths?: number
    dateOfBirth?: string
  }): Promise<Member> {
    const payload = {
      email: data.email,
      first_name: data.firstName,
      last_name: data.lastName,
      phone: data.phone,
      address: data.address,
      notes: data.notes,
      membership_type: data.membershipType,
      membership_tier: data.membershipTier || "standard",
      expiry_months: data.expiryMonths || 12,
      date_of_birth: data.dateOfBirth,
    }
    return apiClient.post<Member>(API_ENDPOINTS.members.register, payload).then(normalizeMember)
  },

  async getPending(): Promise<PaginatedResponse<Member>> {
    return apiClient.get<PaginatedResponse<Member>>(API_ENDPOINTS.members.pending).then((response) => ({
      ...response,
      items: response.items.map(normalizeMember),
    }))
  },

  async approveMember(memberId: string, payload?: MembershipActionPayload): Promise<Member> {
    return apiClient.post<Member>(
      API_ENDPOINTS.members.approve.replace(":id", memberId),
      payload || {}
    ).then(normalizeMember)
  },

  async rejectMember(memberId: string, payload?: MembershipActionPayload): Promise<Member> {
    return apiClient.post<Member>(
      API_ENDPOINTS.members.reject.replace(":id", memberId),
      payload || {}
    ).then(normalizeMember)
  },

  async resubmitMember(memberId: string, payload: MemberResubmitPayload): Promise<Member> {
    return apiClient.post<Member>(
      API_ENDPOINTS.members.resubmit.replace(":id", memberId),
      {
        email: payload.email,
        first_name: payload.firstName,
        last_name: payload.lastName,
        phone: payload.phone,
        address: payload.address,
        notes: payload.notes,
        date_of_birth: payload.dateOfBirth,
        membership_type: payload.membershipType,
        membership_tier: payload.membershipTier,
        expiry_months: payload.expiryMonths,
        comment: payload.comment,
      }
    ).then(normalizeMember)
  },

  async suspendMember(memberId: string, payload?: MembershipActionPayload): Promise<Member> {
    return apiClient.post<Member>(
      API_ENDPOINTS.members.suspend.replace(":id", memberId),
      payload || {}
    ).then(normalizeMember)
  },

  async reactivateMember(memberId: string, payload?: MembershipActionPayload): Promise<Member> {
    return apiClient.post<Member>(
      API_ENDPOINTS.members.reactivate.replace(":id", memberId),
      payload || {}
    ).then(normalizeMember)
  },

  async getById(memberId: string): Promise<Member> {
    return apiClient.get<Member>(
      API_ENDPOINTS.members.get.replace(":id", memberId)
    ).then(normalizeMember)
  },

  async getByUserId(userId: string): Promise<Member> {
    return apiClient.get<Member>(
      API_ENDPOINTS.members.getByUser.replace(":userId", userId)
    ).then(normalizeMember)
  },

  async getByMembershipNumber(membershipNumber: string): Promise<Member> {
    return apiClient.get<Member>(
      API_ENDPOINTS.members.getByMembership.replace(":number", membershipNumber)
    ).then(normalizeMember)
  },

  async list(
    skip: number = 0,
    limit: number = 10,
    filters?: {
      status?: string
      membershipType?: string
    }
  ): Promise<PaginatedResponse<Member>> {
    const params = new URLSearchParams()
    params.append("skip", skip.toString())
    params.append("limit", limit.toString())
    if (filters?.status) params.append("status", filters.status)
    if (filters?.membershipType) params.append("membership_type", filters.membershipType)

    return apiClient.get<PaginatedResponse<Member>>(
      `${API_ENDPOINTS.members.list}?${params.toString()}`
    ).then((response) => ({
      ...response,
      items: response.items.map(normalizeMember),
    }))
  },

  async updateProfile(
    memberId: string,
    data: {
      bio?: string
      profilePhotoUrl?: string
      organization?: string
      position?: string
      department?: string
      newsletterSubscription?: boolean
      eventNotifications?: boolean
      communicationLanguage?: string
    }
  ): Promise<Member> {
    return apiClient.put<Member>(
      API_ENDPOINTS.members.updateProfile.replace(":id", memberId),
      data
    ).then(normalizeMember)
  },

  async renewMembership(memberId: string, months: number = 12): Promise<Member> {
    return apiClient.post<Member>(
      API_ENDPOINTS.members.renew.replace(":id", memberId),
      { months }
    ).then(normalizeMember)
  },

  async upgradeTier(memberId: string, newTier: string): Promise<Member> {
    return apiClient.post<Member>(
      API_ENDPOINTS.members.upgradeTier.replace(":id", memberId),
      { new_tier: newTier }
    ).then(normalizeMember)
  },

  async activateMember(memberId: string): Promise<Member> {
    return apiClient.post<Member>(
      API_ENDPOINTS.members.activate.replace(":id", memberId)
    ).then(normalizeMember)
  },

  async deactivateMember(memberId: string): Promise<Member> {
    return apiClient.post<Member>(
      API_ENDPOINTS.members.deactivate.replace(":id", memberId)
    ).then(normalizeMember)
  },

  async markAsAlumni(memberId: string): Promise<Member> {
    return apiClient.post<Member>(
      API_ENDPOINTS.members.alumni.replace(":id", memberId)
    ).then(normalizeMember)
  },

  async deleteMember(memberId: string): Promise<void> {
    await apiClient.delete(API_ENDPOINTS.members.delete.replace(":id", memberId))
  },

  async assignRole(memberId: string, role: string): Promise<{ roles: string[] }> {
    return apiClient.post<{ roles: string[] }>(
      API_ENDPOINTS.users.roles.replace(":id", memberId),
      { role }
    )
  },

  async removeRole(memberId: string, role: string): Promise<{ roles: string[] }> {
    return apiClient.delete<{ roles: string[] }>(
      `${API_ENDPOINTS.users.roles.replace(":id", memberId)}/${encodeURIComponent(role)}`
    )
  },

  async getActivity(memberId: string): Promise<{
    memberId: string
    meetingsAttended: number
    activitiesParticipated: number
    documentsContributed: number
    totalContributionHours: number
    lastActiveAt?: string
  }> {
    return apiClient.get(
      API_ENDPOINTS.members.activity.replace(":id", memberId)
    )
  },

  async getStatistics(): Promise<{
    totalMembers: number
    activeMembers: number
    inactiveMembers: number
    suspendedMembers: number
    membersByType: Record<string, number>
    membersByTier: Record<string, number>
    totalContributionHours: number
    averageMeetingsAttended: number
  }> {
    return apiClient
      .get(API_ENDPOINTS.members.statistics)
      .then(normalizeMemberStatistics)
  },

  async getExpiringMemberships(days: number = 30): Promise<Array<{
    memberId: string
    email: string
    fullName: string
    membershipNumber: string
    expiryDate: string
    daysUntilExpiry: number
  }>> {
    return apiClient.get(
      `${API_ENDPOINTS.members.expiring}?days=${days}`
    )
  },
}
