"use client"

import React, { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { useMember, useApproveMember, useRejectMember, useSuspendMember, useReactivateMember, useDeactivateMember, useMarkMemberAsAlumni, useRenewMembership, useAssignMemberRole, useRemoveMemberRole, useDeleteMember } from "@/hooks/use-members"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { documentService } from "@/services"
import type { Document as MemberDocument } from "@/types"
import { API_CONFIG } from "@/lib/config"
import { FileText, Users, CheckCircle2, AlertTriangle, Download, X, QrCode } from "lucide-react"

export function MemberProfile() {
  const params = useParams()
  const memberId = params.id as string
  const { data: member, isLoading } = useMember(memberId)
  const approveMemberMutation = useApproveMember()
  const rejectMemberMutation = useRejectMember()
  const suspendMemberMutation = useSuspendMember()
  const reactivateMemberMutation = useReactivateMember()
  const deactivateMemberMutation = useDeactivateMember()
  const markAsAlumniMutation = useMarkMemberAsAlumni()
  const renewMembershipMutation = useRenewMembership()
  const assignRoleMutation = useAssignMemberRole()
  const removeRoleMutation = useRemoveMemberRole()
  const deleteMemberMutation = useDeleteMember()
  const router = useRouter()
  const [internalNotes, setInternalNotes] = useState("")
  const [actionMessage, setActionMessage] = useState<string | null>(null)
  const [documents, setDocuments] = useState<MemberDocument[]>([])
  const [documentsLoading, setDocumentsLoading] = useState(false)
  const [documentsError, setDocumentsError] = useState<string | null>(null)
  const [previewDocument, setPreviewDocument] = useState<MemberDocument | null>(null)
  const [showSuspendModal, setShowSuspendModal] = useState(false)
  const [suspendReason, setSuspendReason] = useState("")

  const renderDate = (dateValue?: string) =>
    dateValue ? new Date(dateValue).toLocaleDateString() : "Not available"

  const renderDocumentDate = (dateValue?: string) => {
    if (!dateValue) return "Unknown date"
    const parsed = new Date(dateValue)
    return Number.isNaN(parsed.getTime()) ? "Unknown date" : parsed.toLocaleDateString()
  }

  const renderBoolean = (value?: boolean) =>
    value === undefined ? "Not available" : value ? "Enabled" : "Disabled"

  const resolveMediaUrl = (value?: string | null) => {
    if (!value) return null
    if (/^https?:\/\//i.test(value)) return value
    if (value.startsWith("/")) return `${API_CONFIG.baseURL}${value}`
    return `${API_CONFIG.baseURL}/${value}`
  }

  const renderValue = (value: unknown, fallback = "Not provided") => {
    if (value === undefined || value === null || value === "") return fallback
    if (typeof value === "boolean") return value ? "Yes" : "No"
    return String(value)
  }

  const documentIds = member?.documentIds ?? []
  const targetUserId = member?.userId ?? memberId
  const memberRoles = ((member as any)?.roles ?? ((member as any)?.role ? [(member as any).role] : ["member"])) as string[]
  const orderedRoles = ["admin", "chairman", "general_secretary", "member"]
  const memberRole = (orderedRoles.find((role) => memberRoles.includes(role)) ?? memberRoles[0] ?? "member").replace(/_/g, " ")
  const normalizeDisplayRole = (role: string) => role.replace(/_/g, " ")
  const memberStatus = (member?.status ?? "").toString().toLowerCase()
  const canReviewApplication = memberStatus === "pending"
  const showQrCard = Boolean(member?.qrToken)
  const resolvedProfilePhotoUrl = resolveMediaUrl(member?.profilePhotoUrl)
  const qrCodeUrl = member?.qrToken
    ? `https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=${encodeURIComponent(member.qrToken)}`
    : null

  const suspendedReason = React.useMemo(() => {
    if (!member?.auditLog) return null
    const entries = Array.isArray(member.auditLog) ? member.auditLog : []
    const last = [...entries].reverse().find((e: any) => (e.action ?? "").toString().toLowerCase() === "suspended")
    return last?.comment ?? null
  }, [member?.auditLog])

  const isPhotoDocument = (document: MemberDocument) => {
    const fileType = document.fileType ?? ""
    const fileUrl = document.fileUrl ?? ""
    return fileType.startsWith("image/") || /\.(png|jpe?g|gif|webp|bmp)$/i.test(fileUrl)
  }

  const displayedDocuments = React.useMemo(() => {
    const list: MemberDocument[] = [...documents]

    if (
      member?.profilePhotoUrl &&
      !list.some(
        (document) =>
          document.fileUrl === member.profilePhotoUrl ||
          document.title.toLowerCase().includes("passport") ||
          document.title.toLowerCase().includes("profile")
      )
    ) {
      list.unshift({
        id: `passport-${member.id}`,
        title: "Passport / Profile Photo",
        description: "Passport photo uploaded during registration",
        fileUrl: member.profilePhotoUrl,
        fileSize: 0,
        fileType: "image/jpeg",
        category: "passport",
        uploadedBy: member.userId,
        uploadedAt: member.updatedAt ?? member.createdAt,
        version: 1,
      })
    }

    return list
  }, [documents, member?.profilePhotoUrl, member?.id, member?.userId, member?.updatedAt, member?.createdAt])

  const documentCount = displayedDocuments.length

  const handleApprove = async () => {
    try {
      await approveMemberMutation.mutateAsync({ id: memberId, comment: internalNotes })
      setActionMessage("Application approved successfully.")
    } catch {
      setActionMessage("Failed to approve application.")
    }
  }

  const handleReject = async () => {
    try {
      await rejectMemberMutation.mutateAsync({ id: memberId, comment: internalNotes })
      setActionMessage("Application rejected successfully.")
    } catch {
      setActionMessage("Failed to reject application.")
    }
  }

  const handleSuspendMembership = async () => {
    setShowSuspendModal(true)
  }

  const handleConfirmSuspend = async () => {
    setShowSuspendModal(false)
    try {
      await suspendMemberMutation.mutateAsync({ id: memberId, comment: suspendReason || undefined })
      setActionMessage("Membership suspended successfully.")
      setSuspendReason("")
    } catch {
      setActionMessage("Failed to suspend membership.")
    }
  }

  const handleCancelSuspend = () => {
    setSuspendReason("")
    setShowSuspendModal(false)
  }

  const handleReactivateMembership = async () => {
    try {
      await reactivateMemberMutation.mutateAsync({ id: memberId, comment: internalNotes })
      setActionMessage("Membership reactivated successfully.")
    } catch {
      setActionMessage("Failed to reactivate membership.")
    }
  }

  const handleDeactivateMembership = async () => {
    try {
      await deactivateMemberMutation.mutateAsync(memberId)
      setActionMessage("Member marked as inactive.")
    } catch {
      setActionMessage("Failed to mark member as inactive.")
    }
  }

  const handleMoveToAlumni = async () => {
    try {
      await markAsAlumniMutation.mutateAsync(memberId)
      setActionMessage("Member moved to alumni successfully.")
    } catch {
      setActionMessage("Failed to move member to alumni.")
    }
  }

  const handleRenewMembership = async () => {
    try {
      await renewMembershipMutation.mutateAsync({ memberId, months: 12 })
      setActionMessage("Membership renewed successfully.")
    } catch {
      setActionMessage("Failed to renew membership.")
    }
  }

  const handleExtendMembershipDuration = async () => {
    try {
      await renewMembershipMutation.mutateAsync({ memberId, months: 24 })
      setActionMessage("Membership duration extended successfully.")
    } catch {
      setActionMessage("Failed to extend membership duration.")
    }
  }

  const handleDeleteMember = async () => {
    const confirmed = window.confirm(
      `Delete member ${member?.fullName ?? "this member"}? This action will soft-delete the member and cannot be undone from the UI.`
    )
    if (!confirmed) return

    try {
      await deleteMemberMutation.mutateAsync(memberId)
      setActionMessage("Member deleted successfully.")
      router.push("/members")
    } catch {
      setActionMessage("Failed to delete member.")
    }
  }

  useEffect(() => {
    if (!documentIds.length) {
      setDocuments([])
      setDocumentsError(null)
      return
    }

    let isMounted = true

    const loadDocuments = async () => {
      setDocumentsLoading(true)
      setDocumentsError(null)

      try {
        const fetchedDocuments = await Promise.all(
          documentIds.map((documentId) => documentService.getById(documentId))
        )

        if (isMounted) {
          setDocuments(fetchedDocuments)
        }
      } catch {
        if (isMounted) {
          setDocumentsError("Unable to load attached documents right now.")
        }
      } finally {
        if (isMounted) {
          setDocumentsLoading(false)
        }
      }
    }

    loadDocuments()

    return () => {
      isMounted = false
    }
  }, [documentIds.join(",")])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-muted-foreground">Loading member profile...</p>
      </div>
    )
  }

  if (!member) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-muted-foreground">Member not found</p>
      </div>
    )
  }

  const confirmRoleAssignment = async (role: string) => {
    if (!targetUserId) {
      setActionMessage("Unable to update role because the linked user account is not available.")
      return
    }

    if (memberRoles.includes(role)) {
      setActionMessage(`Member is already assigned the ${normalizeDisplayRole(role)} role.`)
      return
    }

    const confirmed = window.confirm(
      `Assign ${normalizeDisplayRole(role)} role to ${member.fullName}? This will update the linked user account.`
    )
    if (!confirmed) {
      return
    }

    try {
      await assignRoleMutation.mutateAsync({ memberId, userId: targetUserId, role })
      setActionMessage(`Role updated to ${normalizeDisplayRole(role)} successfully.`)
    } catch {
      setActionMessage("Failed to update role.")
    }
  }

  const handleRemoveRole = async () => {
    if (!targetUserId) {
      setActionMessage("Unable to update role because the linked user account is not available.")
      return
    }

    const elevatedRoles = memberRoles.filter((role) => ["admin", "chairman", "general_secretary"].includes(role))

    if (elevatedRoles.length === 0) {
      setActionMessage("Member is already using the default role.")
      return
    }

    try {
      for (const role of elevatedRoles) {
        await removeRoleMutation.mutateAsync({ memberId, userId: targetUserId, role })
      }
      setActionMessage(`Removed elevated role${elevatedRoles.length > 1 ? "s" : ""} successfully.`)
    } catch {
      setActionMessage("Failed to remove role.")
    }
  }

  return (
    <div className="space-y-8">
      {previewDocument ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-4">
          <div className="w-full max-w-5xl rounded-3xl border border-border bg-background p-4 shadow-2xl">
            <div className="mb-4 flex items-center justify-between gap-3">
              <div>
                <h3 className="text-lg font-semibold">{previewDocument.title}</h3>
                <p className="text-sm text-muted-foreground">{previewDocument.category.replace(/_/g, " ")}</p>
              </div>
              <Button variant="outline" size="sm" onClick={() => setPreviewDocument(null)}>
                <X className="mr-2 h-4 w-4" />
                Close
              </Button>
            </div>

            <div className="overflow-hidden rounded-2xl border border-border bg-muted/40 p-2">
              {(() => {
                const fileType = previewDocument.fileType ?? ""
                const fileUrl = previewDocument.fileUrl ?? ""

                if (fileType.startsWith("image/")) {
                  return (
                    <img
                      src={fileUrl}
                      alt={previewDocument.title}
                      className="max-h-[70vh] w-full object-contain"
                    />
                  )
                }

                if (fileType.includes("pdf")) {
                  return (
                    <iframe
                      src={fileUrl}
                      title={previewDocument.title}
                      className="h-[70vh] w-full rounded-xl border-0"
                    />
                  )
                }

                return (
                  <div className="flex min-h-[40vh] items-center justify-center rounded-xl border border-dashed border-border bg-background/80 px-6 text-center">
                    <div>
                      <p className="font-medium">Preview is not available for this file type.</p>
                      <p className="mt-2 text-sm text-muted-foreground">You can still download the file to view it locally.</p>
                    </div>
                  </div>
                )
              })()}
            </div>
          </div>
        </div>
      ) : null}
      {actionMessage ? (
        <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm font-medium text-emerald-800 shadow-sm">
          {actionMessage}
        </div>
      ) : null}

      <div className="rounded-3xl border border-border bg-card p-6 shadow-sm">
        <div className="flex flex-col gap-6 xl:flex-row xl:items-center xl:justify-between">
          <div className="flex items-center gap-5">
            <div className="relative h-28 w-28 overflow-hidden rounded-full border border-border bg-slate-100">
              {resolvedProfilePhotoUrl ? (
                <img
                  src={resolvedProfilePhotoUrl}
                  alt={`${member.fullName} profile photo`}
                  className="h-full w-full object-cover"
                  onError={(event) => {
                    const target = event.currentTarget as HTMLImageElement
                    target.style.display = "none"
                  }}
                />
              ) : (
                <div className="flex h-full w-full items-center justify-center bg-slate-100 text-sm text-muted-foreground">
                  No photo
                </div>
              )}
            </div>
            <div>
              <h1 className="text-3xl font-bold tracking-tight">{member.fullName}</h1>
              <p className="text-muted-foreground mt-1">{member.email}</p>
              <div className="mt-3 grid gap-2 text-sm text-muted-foreground sm:grid-cols-2">
                <span>{member.phone ?? "No phone"}</span>
                <span>Role: {memberRole}</span>
              </div>
            </div>
          </div>

          <div className="grid gap-3 text-sm text-muted-foreground">
            <div>
              <p className="text-xs uppercase tracking-[0.24em]">Account Status</p>
              <p className="mt-1 font-semibold capitalize">{member.status}</p>
              {member.status === "suspended" && suspendedReason ? (
                <p className="mt-1 text-sm text-destructive">Reason: {suspendedReason}</p>
              ) : null}
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.24em]">Registered On</p>
              <p className="mt-1 font-semibold">{renderDate(member.createdAt)}</p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.24em]">Last Active</p>
              <p className="mt-1 font-semibold">{renderDate(member.lastActiveAt ?? member.approvedAt ?? undefined)}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid gap-4 xl:grid-cols-[1.4fr_0.95fr]">
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Personal Information</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 md:grid-cols-2">
              <div>
                <p className="text-sm text-muted-foreground">First Name</p>
                <p className="font-semibold">{renderValue(member.firstName)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Last Name</p>
                <p className="font-semibold">{renderValue(member.lastName)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Email</p>
                <p className="font-semibold">{renderValue(member.email)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Phone</p>
                <p className="font-semibold">{renderValue(member.phone)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Organization</p>
                <p className="font-semibold">{renderValue(member.organization)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Position</p>
                <p className="font-semibold">{renderValue(member.position)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Department</p>
                <p className="font-semibold">{renderValue(member.department)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Preferred Language</p>
                <p className="font-semibold">{renderValue(member.communicationLanguage?.toUpperCase())}</p>
              </div>
              <div className="md:col-span-2">
                <p className="text-sm text-muted-foreground">Address</p>
                <p className="font-semibold">{renderValue(member.address)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Emergency Contact</p>
                <p className="font-semibold">{renderValue(member.emergencyContactName)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Emergency Contact Phone</p>
                <p className="font-semibold">{renderValue(member.emergencyContactPhone)}</p>
              </div>
              <div className="md:col-span-2">
                <p className="text-sm text-muted-foreground">Bio</p>
                <p className="font-semibold whitespace-pre-line">{renderValue(member.bio)}</p>
              </div>
              <div className="md:col-span-2">
                <p className="text-sm text-muted-foreground">Notes</p>
                <p className="font-semibold whitespace-pre-line">{renderValue(member.notes)}</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Membership & Administrative Details</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 md:grid-cols-2">
              <div>
                <p className="text-sm text-muted-foreground">Membership Number</p>
                <p className="font-semibold">{renderValue(member.membershipNumber)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Application Status</p>
                <p className="font-semibold capitalize">{renderValue(member.status)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Membership Type</p>
                <p className="font-semibold capitalize">{renderValue(member.membershipType)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Membership Tier</p>
                <p className="font-semibold capitalize">{renderValue(member.membershipTier)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Requested Duration</p>
                <p className="font-semibold">{member.requestedExpiryMonths ?? "N/A"} Months</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Membership Expiry</p>
                <p className="font-semibold">{renderDate(member.membershipExpiryDate)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Joined Date</p>
                <p className="font-semibold">{renderDate(member.joinedDate)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Submitted On</p>
                <p className="font-semibold">{renderDate(member.submittedAt)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Newsletter</p>
                <p className="font-semibold">{renderBoolean(member.newsletterSubscription)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Event Notifications</p>
                <p className="font-semibold">{renderBoolean(member.eventNotifications)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Card Status</p>
                <p className="font-semibold">{renderValue(member.cardStatus)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">User ID</p>
                <p className="font-semibold">{renderValue(member.userId)}</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Documents</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                {documentsLoading ? (
                  <p className="text-sm text-muted-foreground">Loading uploaded documents…</p>
                ) : documentsError ? (
                  <p className="text-sm text-destructive">{documentsError}</p>
                ) : displayedDocuments.length > 0 ? (
                  displayedDocuments.map((document) => {
                    const isPhoto = isPhotoDocument(document)

                    return (
                      <div key={document.id} className="rounded-xl border border-border bg-muted/80 p-4">
                        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                          <div>
                            <p className="font-semibold">{document.title}</p>
                            <p className="text-sm text-muted-foreground">
                              {document.category.replace(/_/g, " ")} • {renderDocumentDate(document.uploadedAt)} • {document.fileType}
                            </p>
                          </div>
                          <a
                            href={document.fileUrl}
                            target="_blank"
                            rel="noreferrer"
                            download
                            className="inline-flex h-9 items-center justify-center rounded-md border border-input bg-background px-3 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground"
                          >
                            <Download className="mr-2 h-4 w-4" />
                            Download
                          </a>
                        </div>

                        {isPhoto ? (
                          <div className="mt-4 overflow-hidden rounded-xl border border-border bg-background/80 p-2">
                            <img
                              src={document.fileUrl}
                              alt={document.title}
                              className="max-h-80 w-full rounded-lg object-contain"
                            />
                          </div>
                        ) : null}
                      </div>
                    )
                  })
                ) : (
                  <p className="text-sm text-muted-foreground">No documents have been uploaded for this member yet.</p>
                )}
              </div>
              <div className="flex flex-wrap items-center justify-between gap-3 border-t border-border pt-4">
                <div>
                  <p className="text-sm text-muted-foreground">Attached Documents</p>
                  <p className="font-semibold">{documentCount}</p>
                </div>
                <div className="text-sm text-muted-foreground">
                  {documentCount > 0 ? "Files are loaded directly from the backend." : "No backend-backed documents available yet."}
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Application Timeline</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {member.auditLog && member.auditLog.length > 0 ? (
                member.auditLog.slice(0, 4).map((entry) => (
                  <div key={entry.timestamp} className="rounded-xl border border-border bg-muted p-4">
                    <div className="flex items-center justify-between gap-2">
                      <p className="text-xs text-muted-foreground">{renderDate(entry.timestamp)}</p>
                      <Badge variant={entry.resultingStatus === "active" ? "success" : "destructive"}>
                        {entry.resultingStatus}
                      </Badge>
                    </div>
                    <p className="mt-2 font-semibold capitalize">{entry.action}</p>
                    {entry.comment ? <p className="mt-1 text-sm text-muted-foreground">{entry.comment}</p> : null}
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted-foreground">No timeline events yet.</p>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="space-y-4">
          {canReviewApplication ? (
            <Card>
              <CardHeader>
                <CardTitle>Review Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-sm text-muted-foreground">
                  This application is still pending review. Approve or reject it from here.
                </p>
                <Button onClick={handleApprove} className="w-full">
                  Approve Application
                </Button>
                <Button variant="outline" onClick={handleReject} className="w-full">
                  Reject Application
                </Button>
              </CardContent>
            </Card>
          ) : null}

          <Card>
            <CardHeader>
              <CardTitle>Review Information</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4">
              <div className="flex items-center gap-3">
                <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                <div>
                  <p className="text-sm text-muted-foreground">Approved At</p>
                  <p className="font-semibold">{renderDate(member.approvedAt)}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Users className="h-4 w-4 text-muted-foreground" />
                <div>
                  <p className="text-sm text-muted-foreground">Approved By</p>
                  <p className="font-semibold">{member.approverId ?? "Not available"}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <FileText className="h-4 w-4 text-muted-foreground" />
                <div>
                  <p className="text-sm text-muted-foreground">Approver Role</p>
                  <p className="font-semibold">{member.approverRole ?? "Not available"}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <AlertTriangle className="h-4 w-4 text-muted-foreground" />
                <div>
                  <p className="text-sm text-muted-foreground">Rejected At</p>
                  <p className="font-semibold">{renderDate(member.rejectedAt)}</p>
                </div>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Review Comments</p>
                <p className="font-semibold">{member.reviewComments ?? "None"}</p>
              </div>
            </CardContent>
          </Card>

          {showQrCard && qrCodeUrl ? (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <QrCode className="h-4 w-4" />
                  Digital Membership QR
                </CardTitle>
              </CardHeader>
              <CardContent className="flex flex-col items-center gap-3">
                <div className="rounded-2xl border border-border bg-white p-4 shadow-sm">
                  <img src={qrCodeUrl} alt={`${member.fullName} QR code`} className="h-40 w-40" />
                </div>
                <div className="text-center">
                  <p className="text-sm text-muted-foreground">Membership ID</p>
                  <p className="font-semibold">{member.membershipId ?? member.membershipNumber}</p>
                  <p className="mt-1 text-xs text-muted-foreground">
                    This QR code is linked to this member and can be used for verification at events.
                  </p>
                </div>
              </CardContent>
            </Card>
          ) : null}

          <Card>
            <CardHeader>
              <CardTitle>Reviewer Internal Notes</CardTitle>
            </CardHeader>
            <CardContent>
              <Textarea
                value={internalNotes}
                onChange={(event) => setInternalNotes(event.target.value)}
                placeholder="Add internal reviewer notes here..."
                className="min-h-[160px]"
              />
            </CardContent>
          </Card>

          {showSuspendModal ? (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
              <div className="w-full max-w-2xl rounded-3xl border border-border bg-background p-6 shadow-2xl">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h2 className="text-xl font-semibold">Suspend Membership</h2>
                    <p className="mt-2 text-sm text-muted-foreground">Add an optional reason for the suspension and confirm to proceed.</p>
                  </div>
                  <Button variant="ghost" size="sm" onClick={handleCancelSuspend}>
                    Cancel
                  </Button>
                </div>
                <div className="mt-6">
                  <label className="block text-sm font-medium text-muted-foreground">Suspension Reason</label>
                  <Textarea
                    value={suspendReason}
                    onChange={(event) => setSuspendReason(event.target.value)}
                    placeholder="Enter reason for suspension (optional)"
                    className="mt-2 min-h-[120px]"
                  />
                </div>
                <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:justify-end">
                  <Button variant="outline" onClick={handleCancelSuspend} className="w-full sm:w-auto">
                    Cancel
                  </Button>
                  <Button onClick={handleConfirmSuspend} className="w-full sm:w-auto">
                    Confirm Suspend
                  </Button>
                </div>
              </div>
            </div>
          ) : null}

          <Card>
            <CardHeader>
              <CardTitle>Application Statistics</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 md:grid-cols-2">
              <div>
                <p className="text-sm text-muted-foreground">Activities Participated</p>
                <p className="text-2xl font-bold">{member.activitiesParticipated}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Meetings Attended</p>
                <p className="text-2xl font-bold">{member.meetingsAttended}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Documents Contributed</p>
                <p className="text-2xl font-bold">{member.documentsContributed}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Contribution Hours</p>
                <p className="text-2xl font-bold">{member.totalContributionHours}</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Management Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-3">
                <p className="text-sm font-semibold uppercase tracking-[0.2em] text-muted-foreground">Role Management</p>
                <p className="text-sm text-muted-foreground">These actions update the linked user account role assignments.</p>
                <Button variant="outline" onClick={() => confirmRoleAssignment("member")} className="w-full">Assign Member Role</Button>
                <Button variant="outline" onClick={handleRemoveRole} className="w-full">Remove Elevated Role</Button>
                <Button variant="outline" onClick={() => confirmRoleAssignment("chairman")} className="w-full">Promote to Chairman</Button>
                <Button variant="outline" onClick={() => confirmRoleAssignment("general_secretary")} className="w-full">Promote to General Secretary</Button>
                <Button variant="outline" onClick={() => confirmRoleAssignment("admin")} className="w-full">Promote to Executive Position</Button>
              </div>

              <div className="space-y-3 border-t border-border pt-4">
                <p className="text-sm font-semibold uppercase tracking-[0.2em] text-muted-foreground">Membership Status Management</p>
                <Button variant="outline" onClick={handleSuspendMembership} className="w-full">Suspend Membership</Button>
                <Button variant="outline" onClick={handleReactivateMembership} className="w-full">Reactivate Membership</Button>
                <Button variant="outline" onClick={handleDeactivateMembership} className="w-full">Mark as Inactive</Button>
                <Button variant="outline" onClick={handleMoveToAlumni} className="w-full">Move to Alumni</Button>
                <Button variant="outline" onClick={handleRenewMembership} className="w-full">Renew Membership</Button>
                <Button variant="outline" onClick={handleExtendMembershipDuration} className="w-full">Extend Membership Duration</Button>
                <Button variant="destructive" onClick={handleDeleteMember} className="w-full">Delete Member</Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
