"use client"

import React from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Search, Plus, MoreHorizontal } from "lucide-react"

const mockAdminUsers = [
  {
    id: "1",
    name: "John Doe",
    email: "john@nans.org",
    role: "Super Admin",
    status: "active",
    createdDate: new Date(2023, 0, 15),
    lastLogin: new Date(Date.now() - 2 * 60 * 60 * 1000),
  },
  {
    id: "2",
    name: "Sarah Johnson",
    email: "sarah@nans.org",
    role: "Admin",
    status: "active",
    createdDate: new Date(2023, 2, 20),
    lastLogin: new Date(Date.now() - 5 * 60 * 60 * 1000),
  },
  {
    id: "3",
    name: "Michael Chen",
    email: "michael@nans.org",
    role: "Admin",
    status: "active",
    createdDate: new Date(2023, 5, 10),
    lastLogin: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
  },
  {
    id: "4",
    name: "Emily Davis",
    email: "emily@nans.org",
    role: "Admin",
    status: "inactive",
    createdDate: new Date(2023, 8, 1),
    lastLogin: new Date(2024, 0, 15),
  },
]

export function AdminUserManagement() {
  const [searchTerm, setSearchTerm] = React.useState("")

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Admin Users</h1>
          <p className="text-muted-foreground mt-2">Manage administrator accounts</p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Add Admin
        </Button>
      </div>

      {/* Search */}
      <Card>
        <CardHeader>
          <CardTitle>Search & Filter</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by name or email..."
                className="pl-10"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <Button variant="outline">Filter</Button>
          </div>
        </CardContent>
      </Card>

      {/* Admin Users Table */}
      <Card>
        <CardHeader>
          <CardTitle>Administrator Accounts</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="border-b">
                <tr>
                  <th className="text-left p-2 font-medium">Name</th>
                  <th className="text-left p-2 font-medium">Email</th>
                  <th className="text-left p-2 font-medium">Role</th>
                  <th className="text-left p-2 font-medium">Status</th>
                  <th className="text-left p-2 font-medium">Last Login</th>
                  <th className="text-left p-2 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {mockAdminUsers.map((user) => (
                  <tr key={user.id} className="hover:bg-muted/50">
                    <td className="p-2 font-medium">{user.name}</td>
                    <td className="p-2 text-muted-foreground text-xs">{user.email}</td>
                    <td className="p-2">
                      <Badge variant="outline">{user.role}</Badge>
                    </td>
                    <td className="p-2">
                      <Badge variant={user.status === "active" ? "success" : "secondary"}>
                        {user.status}
                      </Badge>
                    </td>
                    <td className="p-2 text-xs text-muted-foreground">
                      {user.lastLogin.toLocaleString()}
                    </td>
                    <td className="p-2">
                      <Button variant="ghost" size="icon">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Admin Roles */}
      <Card>
        <CardHeader>
          <CardTitle>Admin Roles</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex justify-between items-start pb-3 border-b">
            <div>
              <p className="font-medium">Super Admin</p>
              <p className="text-sm text-muted-foreground">Full system access and user management</p>
            </div>
            <Badge>1 user</Badge>
          </div>
          <div className="flex justify-between items-start pb-3 border-b">
            <div>
              <p className="font-medium">Admin</p>
              <p className="text-sm text-muted-foreground">Member management and approvals</p>
            </div>
            <Badge>3 users</Badge>
          </div>
          <div className="flex justify-between items-start">
            <div>
              <p className="font-medium">Moderator</p>
              <p className="text-sm text-muted-foreground">Content and activity moderation</p>
            </div>
            <Badge>0 users</Badge>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
