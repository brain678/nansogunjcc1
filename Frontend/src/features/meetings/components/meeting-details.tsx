"use client"

import React from "react"
import { useParams } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Calendar, MapPin, Users, Clock, Download } from "lucide-react"

const mockMeetingDetails = {
  id: "1",
  title: "Monthly General Meeting",
  date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
  time: "3:00 PM",
  duration: "2 hours",
  location: "NANS Headquarters, Main Hall",
  description: "Regular monthly meeting for all members to discuss organizational updates and initiatives.",
  attendees: 45,
  maxAttendees: 100,
  status: "scheduled",
  agenda: [
    "Opening remarks and approval of minutes",
    "Financial report Q1 2024",
    "Membership updates",
    "New initiatives and projects",
    "Open discussion",
  ],
  speakers: [
    { name: "John Doe", title: "President", topic: "Opening Remarks" },
    { name: "Jane Smith", title: "Treasurer", topic: "Financial Report" },
    { name: "Michael Brown", title: "Secretary", topic: "Membership Updates" },
  ],
  attendeeList: [
    { id: "1", name: "Sarah Johnson", membershipNumber: "MEM001", checkedIn: true },
    { id: "2", name: "Michael Chen", membershipNumber: "MEM002", checkedIn: true },
    { id: "3", name: "Emily Davis", membershipNumber: "MEM003", checkedIn: false },
    { id: "4", name: "Robert Wilson", membershipNumber: "MEM004", checkedIn: true },
    { id: "5", name: "Jessica Anderson", membershipNumber: "MEM005", checkedIn: false },
  ],
}

export function MeetingDetails() {
  const params = useParams()
  const meetingId = params.id

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{mockMeetingDetails.title}</h1>
          <Badge className="mt-2">{mockMeetingDetails.status}</Badge>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" />
            Download Minutes
          </Button>
          <Button>Edit Meeting</Button>
        </div>
      </div>

      {/* Meeting Info */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-muted-foreground mb-2">
              <Calendar className="h-4 w-4" />
              <span className="text-sm">Date</span>
            </div>
            <p className="font-semibold">{mockMeetingDetails.date.toLocaleDateString()}</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-muted-foreground mb-2">
              <Clock className="h-4 w-4" />
              <span className="text-sm">Time</span>
            </div>
            <p className="font-semibold">{mockMeetingDetails.time}</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-muted-foreground mb-2">
              <MapPin className="h-4 w-4" />
              <span className="text-sm">Location</span>
            </div>
            <p className="font-semibold text-sm">{mockMeetingDetails.location.split(",")[0]}</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-muted-foreground mb-2">
              <Users className="h-4 w-4" />
              <span className="text-sm">Attendees</span>
            </div>
            <p className="font-semibold">
              {mockMeetingDetails.attendees}/{mockMeetingDetails.maxAttendees}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Description */}
      <Card>
        <CardHeader>
          <CardTitle>About This Meeting</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">{mockMeetingDetails.description}</p>
        </CardContent>
      </Card>

      {/* Agenda */}
      <Card>
        <CardHeader>
          <CardTitle>Agenda</CardTitle>
        </CardHeader>
        <CardContent>
          <ol className="space-y-2 list-decimal list-inside">
            {mockMeetingDetails.agenda.map((item, index) => (
              <li key={index} className="text-sm">
                {item}
              </li>
            ))}
          </ol>
        </CardContent>
      </Card>

      {/* Speakers */}
      <Card>
        <CardHeader>
          <CardTitle>Speakers</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {mockMeetingDetails.speakers.map((speaker, idx) => (
            <div key={idx} className="flex justify-between items-start pb-2 border-b last:border-0">
              <div>
                <p className="font-medium">{speaker.name}</p>
                <p className="text-sm text-muted-foreground">{speaker.title}</p>
              </div>
              <Badge variant="outline">{speaker.topic}</Badge>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Attendance */}
      <Card>
        <CardHeader>
          <CardTitle>Attendance Records</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="border-b">
                <tr>
                  <th className="text-left p-2 font-medium">Name</th>
                  <th className="text-left p-2 font-medium">Membership #</th>
                  <th className="text-left p-2 font-medium">Check-in Status</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {mockMeetingDetails.attendeeList.map((attendee) => (
                  <tr key={attendee.id} className="hover:bg-muted/50">
                    <td className="p-2">{attendee.name}</td>
                    <td className="p-2 font-mono text-xs">{attendee.membershipNumber}</td>
                    <td className="p-2">
                      <Badge variant={attendee.checkedIn ? "success" : "warning"}>
                        {attendee.checkedIn ? "✓ Checked In" : "⏳ Pending"}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
