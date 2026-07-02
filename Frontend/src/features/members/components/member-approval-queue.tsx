"use client"

import { useMemo, useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Mail, Phone, MapPin, Check, X, AlertTriangle, ChevronDown, FileText, Users } from "lucide-react"
import Link from "next/link"
import { dateUtils } from "@/lib/utils"
import { Member } from "@/types"
import usePendingMembers, { useApproveMember, useRejectMember } from "@/hooks/use-members"

const renderStatusBadge = (status: string) => {
  switch (status) {
    case "approved":
      return <Badge variant="secondary">Approved</Badge>
    case "rejected":
      return <Badge variant="destructive">Rejected</Badge>
    case "pending":
      return <Badge variant="outline">Pending</Badge>
    default:
      return <Badge variant="outline">{status}</Badge>
  }
}

const getLatestAuditAction = (app: Member) => {
  const entries = app.auditLog ?? []
  const lastEntry = entries.length ? entries[entries.length - 1] : null
  return (lastEntry?.action ?? "").toString().toLowerCase()
}

export function MemberApprovalQueue() {
  const pendingQuery = usePendingMembers()
  const approve = useApproveMember()
  const reject = useRejectMember()
  const items = pendingQuery.data?.items || []
  const [comments, setComments] = useState<Record<string, string>>({})
  const [openDetails, setOpenDetails] = useState<Record<string, boolean>>({})

  const hasPendingItems = useMemo(() => items.length > 0, [items.length])

  const duplicateWarnings = useMemo(() => {
    const emailCounts = new Map<string, number>()
    const membershipCounts = new Map<string, number>()

    items.forEach((app) => {
      if (app.email) {
        emailCounts.set(app.email, (emailCounts.get(app.email) ?? 0) + 1)
      }
      if (app.membershipNumber) {
        membershipCounts.set(app.membershipNumber, (membershipCounts.get(app.membershipNumber) ?? 0) + 1)
      }
    })

    return items.reduce<Record<string, string>>((acc, app) => {
      const hasEmailDuplicate = app.email && (emailCounts.get(app.email) ?? 0) > 1
      const hasMembershipDuplicate = app.membershipNumber && (membershipCounts.get(app.membershipNumber) ?? 0) > 1

      if (hasEmailDuplicate && hasMembershipDuplicate) {
        acc[app.id] = "Duplicate email and membership number found in pending queue."
      } else if (hasEmailDuplicate) {
        acc[app.id] = "Duplicate email found in pending queue."
      } else if (hasMembershipDuplicate) {
        acc[app.id] = "Duplicate membership number found in pending queue."
      }
      return acc
    }, {})
  }, [items])

  const handleCommentChange = (memberId: string, value: string) => {
    setComments((prev) => ({ ...prev, [memberId]: value }))
  }

  const toggleDetails = (memberId: string) => {
    setOpenDetails((prev) => ({ ...prev, [memberId]: !prev[memberId] }))
  }

  const renderSubmittedDate = (app: Member) => {
    if (app.submittedAt) {
      return dateUtils.formatDateTime(app.submittedAt)
    }
    return app.createdAt ? dateUtils.formatDateTime(app.createdAt) : "Unknown"
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Approve Applications</h1>
        <p className="text-muted-foreground mt-2">Review and approve pending member applications with reviewer notes, audit history, and content warnings.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Pending</p>
            <p className="text-3xl font-bold mt-2">{pendingQuery.data?.total ?? items.length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Queue Age</p>
            <p className="text-3xl font-bold mt-2">{items.length ? `${Math.max(1, Math.floor((Date.now() - new Date(items[0].submittedAt || items[0].createdAt).getTime()) / 86400000))}d` : "—"}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Review Notes</p>
            <p className="text-3xl font-bold mt-2">{Object.keys(comments).filter((key) => comments[key]?.trim()).length}</p>
          </CardContent>
        </Card>
      </div>

      <div className="space-y-4">
        {pendingQuery.isLoading && <div>Loading pending applications...</div>}
        {pendingQuery.isError && <div className="text-destructive">Failed to load pending applications.</div>}

        {!pendingQuery.isLoading && !pendingQuery.isError && !hasPendingItems && (
          <div className="rounded-lg border border-border bg-muted p-6 text-muted-foreground">
            There are no pending member applications at this time.
          </div>
        )}

        {items.map((app) => (
          <Card key={app.id}>
            <CardContent className="pt-6">
              <div className="flex flex-col gap-4">
                <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
                  <div className="flex-1 space-y-3">
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="text-lg font-semibold">{app.fullName || `${app.firstName} ${app.lastName}`}</h3>
                      {renderStatusBadge(app.status)}
                      {getLatestAuditAction(app) === "resubmitted" ? (
                        <Badge variant="secondary" className="border-blue-200 bg-blue-50 text-blue-700">
                          Resubmitted
                        </Badge>
                      ) : null}
                    </div>

                    <div className="grid gap-2 text-sm text-muted-foreground sm:grid-cols-2">
                      <div className="flex items-center gap-2">
                        <Mail className="h-4 w-4" />
                        <span>{app.email}</span>
                      </div>
                      {app.phone && (
                        <div className="flex items-center gap-2">
                          <Phone className="h-4 w-4" />
                          <span>{app.phone}</span>
                        </div>
                      )}
                      <div className="flex items-center gap-2">
                        <FileText className="h-4 w-4" />
                        <span>{app.membershipNumber}</span>
                      </div>
                      <div>
                        <span className="font-medium">Submitted:</span> {renderSubmittedDate(app)}
                      </div>
                    </div>

                    <div className="flex flex-wrap items-center gap-2">
                      <Badge variant="outline">{app.membershipType}</Badge>
                      <Badge variant="outline">{app.membershipTier}</Badge>
                      {app.organization && <Badge variant="secondary">{app.organization}</Badge>}
                    </div>
                    <div className="grid gap-2 text-sm text-muted-foreground sm:grid-cols-2">
                      <div>
                        <span className="font-medium">Requested expiry:</span> {app.requestedExpiryMonths ?? 12} mo
                      </div>
                      <div>
                        <span className="font-medium">Preferred language:</span> {app.communicationLanguage?.toUpperCase() ?? "N/A"}
                      </div>
                    </div>

                    {app.reviewComments && (
                      <div className="rounded-md border border-border bg-background p-3 text-sm text-muted-foreground">
                        <div className="font-medium text-foreground">Previous review comment</div>
                        <p>{app.reviewComments}</p>
                      </div>
                    )}

                    {app.approverRole && (
                      <div className="text-sm text-muted-foreground">
                        Last review by <span className="font-medium text-foreground">{app.approverRole}</span>
                      </div>
                    )}

                    {app.department && (
                      <div className="rounded-md border border-border bg-background px-3 py-2 text-sm text-muted-foreground">
                        <div className="font-medium text-foreground">Department</div>
                        <p>{app.department}</p>
                      </div>
                    )}
                    {app.addresses?.length ? (
                      <div className="rounded-md border border-border bg-background px-3 py-2 text-sm text-muted-foreground">
                        <div className="flex items-center gap-2 font-medium text-foreground">
                          <MapPin className="h-4 w-4" />
                          <span>Address</span>
                        </div>
                        <p>{app.addresses[0].street}, {app.addresses[0].city}, {app.addresses[0].state} {app.addresses[0].zipCode}</p>
                        {app.addresses.length > 1 && <p className="text-xs text-muted-foreground">+{app.addresses.length - 1} more</p>}
                      </div>
                    ) : null}
                    {(app.emergencyContactName || app.emergencyContactPhone) && (
                      <div className="rounded-md border border-border bg-background px-3 py-2 text-sm text-muted-foreground">
                        <div className="flex items-center gap-2 font-medium text-foreground">
                          <Users className="h-4 w-4" />
                          <span>Emergency contact</span>
                        </div>
                        {app.emergencyContactName && <p>{app.emergencyContactName}</p>}
                        {app.emergencyContactPhone && <p className="text-xs text-muted-foreground">{app.emergencyContactPhone}</p>}
                      </div>
                    )}
                    <div className="grid gap-2 sm:grid-cols-2">
                      <div className="rounded-md border border-border bg-background px-3 py-2 text-sm text-muted-foreground">
                        <div className="font-medium text-foreground">Newsletter</div>
                        <p>{app.newsletterSubscription ? "Subscribed" : "Unsubscribed"}</p>
                      </div>
                      <div className="rounded-md border border-border bg-background px-3 py-2 text-sm text-muted-foreground">
                        <div className="font-medium text-foreground">Events</div>
                        <p>{app.eventNotifications ? "Enabled" : "Disabled"}</p>
                      </div>
                    </div>
                    {duplicateWarnings[app.id] && (
                      <div className="rounded-md border border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-800">
                        <div className="flex items-start gap-2">
                          <AlertTriangle className="h-4 w-4 shrink-0" />
                          <p>{duplicateWarnings[app.id]}</p>
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="flex flex-col gap-2">
                    <Link href={`/members/${app.id}`}>
                      <Button size="sm" variant="outline" className="gap-1">
                        <FileText className="h-4 w-4" />
                        Review details
                      </Button>
                    </Link>
                    <Button
                      size="sm"
                      className="gap-1"
                      disabled={approve.isPending}
                      onClick={() => approve.mutate({ id: app.id, comment: comments[app.id] })}
                    >
                      <Check className="h-4 w-4" />
                      {approve.isPending ? "Approving..." : "Approve"}
                    </Button>
                    <Button
                      size="sm"
                      variant="destructive"
                      className="gap-1"
                      disabled={reject.isPending || !(comments[app.id] || "").trim()}
                      onClick={() => reject.mutate({ id: app.id, comment: comments[app.id] })}
                    >
                      <X className="h-4 w-4" />
                      {reject.isPending ? "Rejecting..." : "Reject"}
                    </Button>
                  </div>
                </div>

                <div className="grid gap-2">
                  <label className="text-sm font-medium text-muted-foreground" htmlFor={`comment-${app.id}`}>
                    Reviewer notes
                  </label>
                  <textarea
                    id={`comment-${app.id}`}
                    value={comments[app.id] || ""}
                    onChange={(event) => handleCommentChange(app.id, event.target.value)}
                    className="min-h-[96px] rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                    placeholder="Required for rejection"
                  />
                  <p className="text-xs text-muted-foreground">A rejection reason is required before the application can be rejected.</p>
                </div>

                <div className="border-t border-border pt-4">
                  <Button
                    type="button"
                    variant="secondary"
                    size="sm"
                    className="gap-2"
                    onClick={() => toggleDetails(app.id)}
                  >
                    <ChevronDown className="h-4 w-4" />
                    {openDetails[app.id] ? "Hide review details" : "View review details"}
                  </Button>

                  {openDetails[app.id] && (
                    <div className="mt-4 space-y-4 rounded-md border border-border bg-muted p-4 text-sm text-muted-foreground">
                      <div className="flex items-center gap-2 font-medium text-foreground">
                        <FileText className="h-4 w-4" />
                        <span>Application review details</span>
                      </div>

                      <div className="grid gap-3 sm:grid-cols-2">
                        <div>
                          <p className="text-xs uppercase tracking-wide text-muted-foreground">Submitted</p>
                          <p className="font-medium">{renderSubmittedDate(app)}</p>
                        </div>
                        <div>
                          <p className="text-xs uppercase tracking-wide text-muted-foreground">Requested expiry</p>
                          <p className="font-medium">{app.requestedExpiryMonths ?? 12} months</p>
                        </div>
                        <div>
                          <p className="text-xs uppercase tracking-wide text-muted-foreground">Preferred language</p>
                          <p className="font-medium">{app.communicationLanguage?.toUpperCase() ?? "N/A"}</p>
                        </div>
                        <div>
                          <p className="text-xs uppercase tracking-wide text-muted-foreground">Membership plan</p>
                          <p className="font-medium">{app.membershipType} / {app.membershipTier}</p>
                        </div>
                      </div>

                      <div className="grid gap-3 sm:grid-cols-2">
                        {app.organization && (
                          <div>
                            <p className="text-xs uppercase tracking-wide text-muted-foreground">Organization</p>
                            <p className="font-medium">{app.organization}</p>
                          </div>
                        )}
                        {app.position && (
                          <div>
                            <p className="text-xs uppercase tracking-wide text-muted-foreground">Position</p>
                            <p className="font-medium">{app.position}</p>
                          </div>
                        )}
                        {app.department && (
                          <div>
                            <p className="text-xs uppercase tracking-wide text-muted-foreground">Department</p>
                            <p className="font-medium">{app.department}</p>
                          </div>
                        )}
                        {app.phone && (
                          <div>
                            <p className="text-xs uppercase tracking-wide text-muted-foreground">Phone</p>
                            <p className="font-medium">{app.phone}</p>
                          </div>
                        )}
                      </div>

                      {app.addresses?.length ? (
                        <div className="rounded-md border border-border bg-background p-3">
                          <p className="text-xs uppercase tracking-wide text-muted-foreground">Addresses</p>
                          {app.addresses.map((address, index) => (
                            <p key={index} className="font-medium">
                              {address.street}, {address.city}, {address.state} {address.zipCode}, {address.country}
                            </p>
                          ))}
                        </div>
                      ) : null}

                      {(app.emergencyContactName || app.emergencyContactPhone) && (
                        <div className="rounded-md border border-border bg-background p-3">
                          <p className="text-xs uppercase tracking-wide text-muted-foreground">Emergency contact</p>
                          {app.emergencyContactName && <p className="font-medium">{app.emergencyContactName}</p>}
                          {app.emergencyContactPhone && <p className="text-sm text-muted-foreground">{app.emergencyContactPhone}</p>}
                        </div>
                      )}

                      <div className="grid gap-3 sm:grid-cols-2">
                        <div className="rounded-md border border-border bg-background p-3">
                          <p className="text-xs uppercase tracking-wide text-muted-foreground">Newsletter</p>
                          <p className="font-medium">{app.newsletterSubscription ? "Subscribed" : "Unsubscribed"}</p>
                        </div>
                        <div className="rounded-md border border-border bg-background p-3">
                          <p className="text-xs uppercase tracking-wide text-muted-foreground">Event notifications</p>
                          <p className="font-medium">{app.eventNotifications ? "Enabled" : "Disabled"}</p>
                        </div>
                      </div>

                      <div className="rounded-md border border-border bg-background p-3">
                        <div className="flex items-center gap-2 font-medium text-foreground">
                          <FileText className="h-4 w-4" />
                          <span>Audit history</span>
                        </div>
                        {app.auditLog?.length ? (
                          app.auditLog.map((entry) => (
                            <div key={entry.timestamp} className="mt-3 rounded-md border border-border bg-muted p-3">
                              <div className="flex flex-col gap-1">
                                <div className="text-xs uppercase tracking-wide text-muted-foreground">{dateUtils.formatDateTime(entry.timestamp)}</div>
                                <div className="font-semibold text-foreground">{entry.action}</div>
                                <div>{entry.comment || "No comment provided."}</div>
                                <div className="text-xs text-muted-foreground">
                                  {entry.performedByRole ? `${entry.performedByRole} • ` : ""}{entry.performedByUserId ?? "System"}
                                </div>
                              </div>
                            </div>
                          ))
                        ) : (
                          <div className="mt-3 rounded-md border border-dashed border-border bg-background px-3 py-2">
                            No audit history available yet.
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
