import { useMutation, useQuery, useQueryClient, UseMutationResult } from "@tanstack/react-query"
import { memberService } from "@/services/members"
import { errorUtils } from "@/lib/utils"
import { useAuthStore } from "@/store/auth"
import { apiClient } from "@/lib/api-client"
import { API_ENDPOINTS } from "@/lib/config"

export const usePendingMembers = () => {
  return useQuery({
    queryKey: ["members", "pending"],
    queryFn: () => memberService.getPending(),
    staleTime: 60_000,
    retry: 1,
  })
}

export const useApproveMember = (): UseMutationResult<
  any,
  Error,
  { id: string; comment?: string },
  unknown
> => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: { id: string; comment?: string }) => memberService.approveMember(payload.id, { comment: payload.comment }),
    onSuccess: (_, variables) => {
      qc.setQueryData(["members", variables.id], (current: any) =>
        current ? { ...current, status: "active", approvedAt: new Date().toISOString() } : current
      )
      qc.invalidateQueries({ queryKey: ["members", variables.id] })
      qc.invalidateQueries({ queryKey: ["members", "pending"] })
      qc.invalidateQueries({ queryKey: ["members"] })
    },
  })
}

export const useRejectMember = (): UseMutationResult<
  any,
  Error,
  { id: string; comment?: string },
  unknown
> => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: { id: string; comment?: string }) => memberService.rejectMember(payload.id, { comment: payload.comment }),
    onSuccess: (_, variables) => {
      qc.setQueryData(["members", variables.id], (current: any) =>
        current ? { ...current, status: "rejected", rejectedAt: new Date().toISOString() } : current
      )
      qc.invalidateQueries({ queryKey: ["members", variables.id] })
      qc.invalidateQueries({ queryKey: ["members", "pending"] })
      qc.invalidateQueries({ queryKey: ["members"] })
    },
  })
}

export const useResubmitMember = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: Parameters<typeof memberService.resubmitMember>[1] & { id: string; memberRecordId?: string }) => {
      const { id, memberRecordId, ...rest } = payload
      return memberService.resubmitMember(id, rest).then((member) => ({ member, memberRecordId }))
    },
    onSuccess: (result, variables) => {
      const memberId = result.memberRecordId || variables.memberRecordId || variables.id
      qc.setQueryData(["members", memberId], (current: any) =>
        current ? { ...current, status: "pending", reviewComments: undefined, rejectedAt: undefined, approverId: undefined, approverRole: undefined } : current
      )
      qc.invalidateQueries({ queryKey: ["members", memberId] })
      qc.invalidateQueries({ queryKey: ["members", "pending"] })
      qc.invalidateQueries({ queryKey: ["members"] })
    },
  })
}

export const useAssignMemberRole = () => {
  const qc = useQueryClient()

  return useMutation<{ roles: string[] }, Error, { memberId: string; userId: string; role: string }>({
    mutationFn: ({ userId, role }) => memberService.assignRole(userId, role),
    onSuccess: (data, variables) => {
      const newRoles = data?.roles ?? [variables.role]
      qc.setQueryData(["members", variables.memberId], (current: any) =>
        current ? { ...current, role: newRoles[0] ?? variables.role, roles: newRoles } : current
      )
      qc.invalidateQueries({ queryKey: ["members", variables.memberId] })
      qc.invalidateQueries({ queryKey: ["members"] })
    },
  })
}

export const useRemoveMemberRole = () => {
  const qc = useQueryClient()

  return useMutation<{ roles: string[] }, Error, { memberId: string; userId: string; role: string }>({
    mutationFn: ({ userId, role }) => memberService.removeRole(userId, role),
    onSuccess: (data, variables) => {
      const newRoles = data?.roles ?? ["member"]
      qc.setQueryData(["members", variables.memberId], (current: any) =>
        current ? { ...current, role: newRoles[0] ?? "member", roles: newRoles } : current
      )
      qc.invalidateQueries({ queryKey: ["members", variables.memberId] })
      qc.invalidateQueries({ queryKey: ["members"] })
    },
  })
}

export const useReactivateMember = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: { id: string; comment?: string }) => memberService.reactivateMember(payload.id, { comment: payload.comment }),
    onSuccess: async (member, variables) => {
      // If the API returns the updated member object (including qrToken), update the cache accordingly.
      if (member && member.qrToken) {
        qc.setQueryData(["members", variables.id], member)
      } else {
        // If the reactivate response does not include a qrToken, fetch the full member record
        // from the backend (which may generate/attach the QR token) and update the cache.
        try {
          const fresh = await memberService.getById(variables.id)
          qc.setQueryData(["members", variables.id], fresh)

          // If the fresh record still lacks a qrToken, attempt a best-effort generation
          // via the identity.generateQr endpoint, then refresh again.
          if (!fresh.qrToken) {
            try {
              await apiClient.post(API_ENDPOINTS.identity.generateQr, { memberId: variables.id })
              const regenerated = await memberService.getById(variables.id)
              qc.setQueryData(["members", variables.id], regenerated)
            } catch (genErr) {
              // ignore generation errors; we already set status above
            }
          }
        } catch (e) {
          qc.setQueryData(["members", variables.id], (current: any) => (current ? { ...current, status: "active" } : current))
        }
      }
      qc.invalidateQueries({ queryKey: ["members", variables.id] })
      qc.invalidateQueries({ queryKey: ["members"] })
    },
  })
}

export default usePendingMembers

export const useMembers = (skip: number = 0, limit: number = 10, filters?: any) => {
  return useQuery({
    queryKey: ["members", skip, limit, filters],
    queryFn: async () => {
      return memberService.list(skip, limit, filters)
    },
    staleTime: 5 * 60 * 1000,
  })
}

export const useMember = (memberId: string) => {
  return useQuery({
    queryKey: ["members", memberId],
    queryFn: async () => {
      return memberService.getById(memberId)
    },
    enabled: !!memberId,
    staleTime: 5 * 60 * 1000,
  })
}

export const useMemberByNumber = (membershipNumber: string) => {
  return useQuery({
    queryKey: ["members", "by-number", membershipNumber],
    queryFn: async () => {
      return memberService.getByMembershipNumber(membershipNumber)
    },
    enabled: !!membershipNumber,
  })
}

export const useMemberActivity = (memberId: string) => {
  return useQuery({
    queryKey: ["members", memberId, "activity"],
    queryFn: async () => {
      return memberService.getActivity(memberId)
    },
    enabled: !!memberId,
    staleTime: 10 * 60 * 1000,
  })
}

export const useMembersStatistics = () => {
  return useQuery({
    queryKey: ["members", "statistics"],
    queryFn: async () => {
      return memberService.getStatistics()
    },
    staleTime: 15 * 60 * 1000,
  })
}

export const useExpiringMemberships = (days: number = 30) => {
  return useQuery({
    queryKey: ["members", "expiring", days],
    queryFn: async () => {
      return memberService.getExpiringMemberships(days)
    },
    staleTime: 30 * 60 * 1000,
  })
}

export const useRegisterMember = () => {
  const queryClient = useQueryClient()
  const { user, setUser } = useAuthStore()

  return useMutation({
    mutationFn: async (data: Parameters<typeof memberService.register>[0]) => {
      return memberService.register(data)
    },
    onSuccess: (member) => {
      if (user) {
        setUser({
          ...user,
          membershipStatus: member.status,
          membershipNumber: member.membershipNumber,
        })
      }
      queryClient.invalidateQueries({ queryKey: ["members"] })
    },
    onError: (error) => {
      console.error("Member registration failed:", errorUtils.getErrorMessage(error))
    },
  })
}

export const useUpdateMemberProfile = (memberId: string) => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: Parameters<typeof memberService.updateProfile>[1]) => {
      return memberService.updateProfile(memberId, data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["members", memberId] })
    },
    onError: (error) => {
      console.error("Update failed:", errorUtils.getErrorMessage(error))
    },
  })
}

export const useSuspendMember = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (payload: { id: string; comment?: string }) => {
      return memberService.suspendMember(payload.id, { comment: payload.comment })
    },
    onSuccess: (_, variables) => {
      const memberId = (variables as any).id
      queryClient.setQueryData(["members", memberId], (current: any) =>
        current ? { ...current, status: "suspended" } : current
      )
      queryClient.invalidateQueries({ queryKey: ["members", memberId] })
      queryClient.invalidateQueries({ queryKey: ["members"] })
    },
  })
}

export const useActivateMember = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (payload: { id: string; comment?: string }) => {
      return memberService.suspendMember(payload.id, { comment: payload.comment })
    },
    onSuccess: (member, variables) => {
      const memberId = (variables as any).id
      queryClient.setQueryData(["members", memberId], (current: any) => {
        if (!current) return { ...member, status: "suspended" }
        return {
          ...current,
          ...member,
          status: "suspended",
          qrToken: current.qrToken ?? member?.qrToken,
          membershipId: current.membershipId ?? member?.membershipId,
          cardStatus: current.cardStatus ?? member?.cardStatus,
        }
      })
      queryClient.invalidateQueries({ queryKey: ["members", memberId] })
      queryClient.invalidateQueries({ queryKey: ["members"] })
    },
  })
}

export const useDeleteMember = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (memberId: string) => {
      return memberService.deleteMember(memberId)
    },
    onSuccess: (_, memberId) => {
      queryClient.invalidateQueries({ queryKey: ["members", memberId] })
      queryClient.invalidateQueries({ queryKey: ["members"] })
    },
  })
}

export const useDeactivateMember = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (memberId: string) => {
      return memberService.deactivateMember(memberId)
    },
    onSuccess: (_, memberId) => {
      queryClient.setQueryData(["members", memberId], (current: any) =>
        current ? { ...current, status: "inactive" } : current
      )
      queryClient.invalidateQueries({ queryKey: ["members", memberId] })
      queryClient.invalidateQueries({ queryKey: ["members"] })
    },
  })
}

export const useMarkMemberAsAlumni = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (memberId: string) => {
      return memberService.markAsAlumni(memberId)
    },
    onSuccess: (_, memberId) => {
      queryClient.setQueryData(["members", memberId], (current: any) =>
        current ? { ...current, status: "resigned" } : current
      )
      queryClient.invalidateQueries({ queryKey: ["members", memberId] })
      queryClient.invalidateQueries({ queryKey: ["members"] })
    },
  })
}

export const useRenewMembership = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ memberId, months }: { memberId: string; months?: number }) => {
      return memberService.renewMembership(memberId, months ?? 12)
    },
    onSuccess: (_, variables) => {
      queryClient.setQueryData(["members", variables.memberId], (current: any) =>
        current ? { ...current, status: current.status || "active" } : current
      )
      queryClient.invalidateQueries({ queryKey: ["members", variables.memberId] })
      queryClient.invalidateQueries({ queryKey: ["members"] })
    },
  })
}
