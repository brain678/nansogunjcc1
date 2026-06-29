"use client"

import React from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useMembersStatistics } from "@/hooks/use-members"
import { Users, Award, Calendar, Activity } from "lucide-react"
import Link from "next/link"

export function AdminDashboard() {
  const { data: stats, isLoading } = useMembersStatistics()

  return (
    <div className="space-y-8">
      <div>
        <div className="flex flex-col gap-3">
          <div>
            <p className="text-sm uppercase tracking-[0.24em] text-muted-foreground">Admin Dashboard</p>
            <h1 className="text-3xl font-bold tracking-tight">Membership Overview</h1>
          </div>
          <p className="text-muted-foreground">
            Welcome back, Administrator. Review the latest membership status and activity counts below.
          </p>
        </div>
      </div>

      <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Total Members</CardTitle>
            <CardDescription>Current membership count</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-semibold">{isLoading ? "-" : stats?.totalMembers ?? 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Active Members</CardTitle>
            <CardDescription>Members currently active</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-semibold">{isLoading ? "-" : stats?.activeMembers ?? 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Suspended Members</CardTitle>
            <CardDescription>Members requiring assistance</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-semibold">{isLoading ? "-" : stats?.suspendedMembers ?? 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Total Hours</CardTitle>
            <CardDescription>Contributed by members</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-semibold">{isLoading ? "-" : Math.round(stats?.totalContributionHours ?? 0)}</div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Manage your platform</CardDescription>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link href="/members">
            <Button variant="outline" className="w-full">
              👥 Manage Members
            </Button>
          </Link>
          <Link href="/members/approve">
            <Button variant="outline" className="w-full">
              ✅ Approve Applications
            </Button>
          </Link>
          <Link href="/admin/audit">
            <Button variant="outline" className="w-full">
              📊 View Audit Logs
            </Button>
          </Link>
        </CardContent>
      </Card>

      {/* Member Distribution */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card>
            <CardHeader>
              <CardTitle>Members by Type</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {Object.entries(stats.membersByType || {}).map(([type, count]) => (
                <div key={type} className="flex justify-between items-center">
                  <span className="text-sm capitalize">{type}</span>
                  <span className="font-semibold">{count}</span>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Members by Tier</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {Object.entries(stats.membersByTier || {}).map(([tier, count]) => (
                <div key={tier} className="flex justify-between items-center">
                  <span className="text-sm capitalize">{tier}</span>
                  <span className="font-semibold">{count}</span>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
