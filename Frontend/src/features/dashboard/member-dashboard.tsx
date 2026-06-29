"use client"

import React from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { User, Calendar, Award, Bell } from "lucide-react"
import Link from "next/link"

export function MemberDashboard() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Welcome Back</h1>
        <p className="text-slate-600 mt-2">Your membership and activity overview</p>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="border-[#008753]/10 bg-white text-foreground">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-900">Membership Status</CardTitle>
            <Award className="h-4 w-4 text-[#008753]" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-[#008753]">Active</div>
            <p className="text-xs text-slate-500 mt-1">Expires in 180 days</p>
          </CardContent>
        </Card>

        <Card className="border-[#008753]/10 bg-white text-foreground">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-900">Member Type</CardTitle>
            <User className="h-4 w-4 text-[#008753]" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-slate-900">Regular</div>
            <p className="text-xs text-slate-500 mt-1">Tier: Gold</p>
          </CardContent>
        </Card>

        <Card className="border-[#008753]/10 bg-white text-foreground">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-900">Meetings Attended</CardTitle>
            <Calendar className="h-4 w-4 text-[#008753]" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-slate-900">12</div>
            <p className="text-xs text-slate-500 mt-1">This year</p>
          </CardContent>
        </Card>

        <Card className="border-[#008753]/10 bg-white text-foreground">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-900">Notifications</CardTitle>
            <Bell className="h-4 w-4 text-[#008753]" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-slate-900">2</div>
            <p className="text-xs text-slate-500 mt-1">Unread messages</p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Links */}
      <Card className="border-[#008753]/10 bg-white text-foreground">
        <CardHeader>
          <CardTitle className="text-slate-900">Quick Links</CardTitle>
          <CardDescription>Access important features</CardDescription>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link href="/my-id-card">
            <Button className="w-full">🎫 My ID Card</Button>
          </Link>
          <Link href="/profile">
            <Button variant="outline" className="w-full">
              👤 My Profile
            </Button>
          </Link>
          <Link href="/meetings">
            <Button variant="outline" className="w-full">
              📅 Meetings
            </Button>
          </Link>
        </CardContent>
      </Card>

      {/* Upcoming Events */}
      <Card className="border-[#008753]/10 bg-white text-foreground">
        <CardHeader>
          <CardTitle className="text-slate-900">Upcoming Events</CardTitle>
          <CardDescription>Events you're invited to</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-start justify-between pb-2 border-b border-slate-200">
            <div>
              <p className="font-medium text-slate-900 text-sm">Monthly General Meeting</p>
              <p className="text-xs text-slate-500">Friday, 3:00 PM</p>
            </div>
            <Badge variant="default">📅 Upcoming</Badge>
          </div>
          <div className="flex items-start justify-between pb-2 border-b border-slate-200">
            <div>
              <p className="font-medium text-slate-900 text-sm">Community Service Project</p>
              <p className="text-xs text-slate-500">Saturday, 9:00 AM</p>
            </div>
            <Badge variant="default">🎯 Upcoming</Badge>
          </div>
          <div className="flex items-start justify-between">
            <div>
              <p className="font-medium text-slate-900 text-sm">Member Networking Event</p>
              <p className="text-xs text-slate-500">Next month</p>
            </div>
            <Badge variant="outline" className="border-[#008753]/30 text-[#008753] bg-white">⏳ Save the date</Badge>
          </div>
        </CardContent>
      </Card>

      {/* Statistics */}
      <Card className="border-[#008753]/10 bg-white text-foreground">
        <CardHeader>
          <CardTitle className="text-slate-900">Your Statistics</CardTitle>
          <CardDescription>Member activity summary</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-sm text-slate-700">Contribution Hours</span>
            <span className="font-semibold text-slate-900">24 hours</span>
          </div>
          <div className="w-full bg-[#E8F7F1] rounded-full h-2">
            <div className="bg-[#008753] h-2 rounded-full" style={{ width: "60%" }} />
          </div>
          <p className="text-xs text-slate-500">60% towards annual goal (40 hours)</p>
        </CardContent>
      </Card>
    </div>
  )
}
