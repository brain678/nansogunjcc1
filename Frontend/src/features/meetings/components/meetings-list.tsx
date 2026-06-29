"use client"

import React, { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Calendar, MapPin, Users, Plus } from "lucide-react"
import Link from "next/link"

const mockMeetings = [
  {
    id: "1",
    title: "Monthly General Meeting",
    date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
    time: "3:00 PM",
    location: "NANS Headquarters",
    attendees: 45,
    status: "scheduled",
  },
  {
    id: "2",
    title: "Executive Committee Meeting",
    date: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000),
    time: "10:00 AM",
    location: "Virtual",
    attendees: 12,
    status: "scheduled",
  },
  {
    id: "3",
    title: "Annual Conference",
    date: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000),
    time: "9:00 AM",
    location: "Convention Center",
    attendees: 200,
    status: "scheduled",
  },
]

export function MeetingsList() {
  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Meetings</h1>
          <p className="text-muted-foreground mt-2">View and manage organization meetings</p>
        </div>
        <Link href="/meetings/create">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Create Meeting
          </Button>
        </Link>
      </div>

      {/* Meetings Cards */}
      <div className="space-y-4">
        {mockMeetings.map((meeting) => (
          <Card key={meeting.id} className="hover:shadow-md transition-shadow">
            <CardContent className="pt-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold">{meeting.title}</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4 text-sm text-muted-foreground">
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4" />
                      <span>
                        {meeting.date.toLocaleDateString()} at {meeting.time}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <MapPin className="h-4 w-4" />
                      <span>{meeting.location}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Users className="h-4 w-4" />
                      <span>{meeting.attendees} attendees</span>
                    </div>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Badge variant="secondary">
                    {meeting.status === "scheduled" ? "📅 Upcoming" : "✅ Completed"}
                  </Badge>
                  <Link href={`/meetings/${meeting.id}`}>
                    <Button variant="outline" size="sm">
                      View
                    </Button>
                  </Link>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
