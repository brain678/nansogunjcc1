"use client"

import React from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useMembersStatistics } from "@/hooks/use-members"
import { Users, Calendar, CheckCircle, FileText } from "lucide-react"
import Link from "next/link"

export function GeneralSecretaryDashboard() {
  const { data: stats, isLoading } = useMembersStatistics()

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">General Secretary Dashboard</h1>
        <p className="text-muted-foreground mt-2">National level organization management</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Members</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{isLoading ? "-" : stats?.totalMembers || 0}</div>
            <p className="text-xs text-muted-foreground mt-1">Nationally</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Approvals</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">12</div>
            <p className="text-xs text-muted-foreground mt-1">Awaiting review</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Upcoming Meetings</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">5</div>
            <p className="text-xs text-muted-foreground mt-1">This month</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Documents</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">42</div>
            <p className="text-xs text-muted-foreground mt-1">In repository</p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>National administration</CardDescription>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link href="/members/approve">
            <Button className="w-full">✅ Approve Members</Button>
          </Link>
          <Link href="/meetings/create">
            <Button variant="outline" className="w-full">
              📅 Create Meeting
            </Button>
          </Link>
          <Link href="/documents">
            <Button variant="outline" className="w-full">
              📄 Manage Documents
            </Button>
          </Link>
        </CardContent>
      </Card>

      {/* Member Status */}
      <Card>
        <CardHeader>
          <CardTitle>Membership Overview</CardTitle>
          <CardDescription>Current member statistics</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex justify-between items-center">
            <span>Active Members</span>
            <Badge variant="success">{stats?.activeMembers || 0}</Badge>
          </div>
          <div className="flex justify-between items-center">
            <span>Inactive Members</span>
            <Badge variant="warning">{stats?.inactiveMembers || 0}</Badge>
          </div>
          <div className="flex justify-between items-center">
            <span>Suspended Members</span>
            <Badge variant="destructive">{stats?.suspendedMembers || 0}</Badge>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
