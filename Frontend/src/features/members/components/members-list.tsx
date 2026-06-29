"use client"

import React, { useState } from "react"
import { useMembers } from "@/hooks/use-members"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Search, Plus } from "lucide-react"
import Link from "next/link"

export function MembersList() {
  const [searchTerm, setSearchTerm] = useState("")
  const [page, setPage] = useState(0)
  const { data: membersResponse, isLoading } = useMembers(page * 10, 10)

  const members = membersResponse?.items || []
  const total = membersResponse?.total || 0

  const statusColors = {
    active: "success",
    inactive: "warning",
    suspended: "destructive",
  } as const

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Members</h1>
          <p className="text-muted-foreground mt-2">Manage organization members</p>
        </div>
        <Link href="/members/create">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Add Member
          </Button>
        </Link>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Search & Filter</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by name, email, or membership number..."
                className="pl-10"
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value)
                  setPage(0)
                }}
              />
            </div>
            <Button variant="outline">Filter</Button>
          </div>
        </CardContent>
      </Card>

      {/* Members Table */}
      <Card>
        <CardHeader>
          <CardTitle>Members List</CardTitle>
          <CardDescription>
            Showing {members.length} of {total} members
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8">
              <p className="text-muted-foreground">Loading members...</p>
            </div>
          ) : members.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-muted-foreground">No members found</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="border-b">
                  <tr>
                    <th className="text-left p-2 font-medium">Name</th>
                    <th className="text-left p-2 font-medium">Email</th>
                    <th className="text-left p-2 font-medium">Membership #</th>
                    <th className="text-left p-2 font-medium">Type</th>
                    <th className="text-left p-2 font-medium">Status</th>
                    <th className="text-left p-2 font-medium">Joined</th>
                    <th className="text-left p-2 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {members.map((member) => (
                    <tr key={member.id} className="hover:bg-muted/50">
                      <td className="p-2 font-medium">
                        {member.firstName} {member.lastName}
                      </td>
                      <td className="p-2 text-muted-foreground">{member.email}</td>
                      <td className="p-2">{member.membershipNumber}</td>
                      <td className="p-2 capitalize">{member.membershipType}</td>
                      <td className="p-2">
                        <Badge
                          variant={
                            statusColors[member.status as keyof typeof statusColors] ||
                            "default"
                          }
                        >
                          {member.status}
                        </Badge>
                      </td>
                      <td className="p-2 text-sm">
                        {new Date(member.joinedDate).toLocaleDateString()}
                      </td>
                      <td className="p-2">
                        <Link href={`/members/${member.id}`}>
                          <Button variant="ghost" size="sm">
                            View
                          </Button>
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Pagination */}
          {total > 10 && (
            <div className="flex items-center justify-between mt-6 pt-6 border-t">
              <p className="text-sm text-muted-foreground">
                Page {page + 1} of {Math.ceil(total / 10)}
              </p>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(Math.max(0, page - 1))}
                  disabled={page === 0}
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(page + 1)}
                  disabled={(page + 1) * 10 >= total}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
