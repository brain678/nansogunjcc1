"use client"

import React from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Users, Calendar, CheckCircle, Activity } from "lucide-react"
import Link from "next/link"

export function ChairmanDashboard() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Chairman Dashboard</h1>
        <p className="text-muted-foreground mt-2">Chapter leadership overview</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Chapter Members</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">48</div>
            <p className="text-xs text-muted-foreground mt-1">Active in chapter</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Approvals</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">3</div>
            <p className="text-xs text-muted-foreground mt-1">Awaiting your review</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Meetings This Month</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">4</div>
            <p className="text-xs text-muted-foreground mt-1">Scheduled</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Activities</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">12</div>
            <p className="text-xs text-muted-foreground mt-1">Ongoing</p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Chapter management</CardDescription>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link href="/members/approve">
            <Button className="w-full">✅ Review Applications</Button>
          </Link>
          <Link href="/meetings/create">
            <Button variant="outline" className="w-full">
              📅 Schedule Meeting
            </Button>
          </Link>
          <Link href="/activities/create">
            <Button variant="outline" className="w-full">
              🎯 Create Activity
            </Button>
          </Link>
        </CardContent>
      </Card>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>Latest chapter events</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-start justify-between pb-2 border-b">
            <div>
              <p className="font-medium text-sm">Monthly General Meeting</p>
              <p className="text-xs text-muted-foreground">Next week on Friday</p>
            </div>
            <Badge>📅 Upcoming</Badge>
          </div>
          <div className="flex items-start justify-between pb-2 border-b">
            <div>
              <p className="font-medium text-sm">New Member Applications</p>
              <p className="text-xs text-muted-foreground">3 pending your approval</p>
            </div>
            <Badge variant="warning">⏳ Pending</Badge>
          </div>
          <div className="flex items-start justify-between">
            <div>
              <p className="font-medium text-sm">Community Service Project</p>
              <p className="text-xs text-muted-foreground">20 members participated</p>
            </div>
            <Badge variant="success">✅ Completed</Badge>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
