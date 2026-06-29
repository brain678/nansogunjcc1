"use client"

import React from "react"
import { useParams } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Calendar, MapPin, Users, Clock, Heart } from "lucide-react"

const mockActivityDetails = {
  id: "1",
  title: "Community Cleanup Drive",
  date: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000),
  time: "9:00 AM",
  duration: "3 hours",
  location: "Central Park",
  description: "Join us for a community service initiative to clean up Central Park and surrounding areas. All members are welcome and encouraged to participate.",
  participants: 32,
  maxParticipants: 50,
  status: "upcoming",
  hoursAwarded: 3,
  category: "Community Service",
  organizer: "Sarah Johnson",
  beneficiary: "Local Environment Fund",
  participantList: [
    { id: "1", name: "John Doe", membershipNumber: "MEM001", checkedIn: false },
    { id: "2", name: "Jane Smith", membershipNumber: "MEM002", checkedIn: false },
    { id: "3", name: "Michael Chen", membershipNumber: "MEM003", checkedIn: true },
    { id: "4", name: "Emily Davis", membershipNumber: "MEM004", checkedIn: false },
  ],
}

export function ActivityDetails() {
  const params = useParams()
  const activityId = params.id

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{mockActivityDetails.title}</h1>
          <div className="flex gap-2 mt-2">
            <Badge>{mockActivityDetails.status}</Badge>
            <Badge variant="outline">{mockActivityDetails.category}</Badge>
            <Badge variant="success">{mockActivityDetails.hoursAwarded} hours</Badge>
          </div>
        </div>
        <Button>Manage Activity</Button>
      </div>

      {/* Activity Info Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-muted-foreground mb-2">
              <Calendar className="h-4 w-4" />
              <span className="text-sm">Date</span>
            </div>
            <p className="font-semibold">{mockActivityDetails.date.toLocaleDateString()}</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-muted-foreground mb-2">
              <Clock className="h-4 w-4" />
              <span className="text-sm">Time</span>
            </div>
            <p className="font-semibold">{mockActivityDetails.time}</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-muted-foreground mb-2">
              <MapPin className="h-4 w-4" />
              <span className="text-sm">Location</span>
            </div>
            <p className="font-semibold text-sm">{mockActivityDetails.location}</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-muted-foreground mb-2">
              <Users className="h-4 w-4" />
              <span className="text-sm">Participants</span>
            </div>
            <p className="font-semibold">
              {mockActivityDetails.participants}/{mockActivityDetails.maxParticipants}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Description */}
      <Card>
        <CardHeader>
          <CardTitle>About This Activity</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-muted-foreground">{mockActivityDetails.description}</p>
          <div className="grid grid-cols-2 gap-4 pt-4 border-t">
            <div>
              <p className="text-sm text-muted-foreground">Organizer</p>
              <p className="font-semibold">{mockActivityDetails.organizer}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Beneficiary</p>
              <p className="font-semibold">{mockActivityDetails.beneficiary}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Participation Benefits */}
      <Card>
        <CardHeader>
          <CardTitle>Contribution Benefits</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center gap-3 pb-2 border-b">
            <Heart className="h-5 w-5 text-red-500" />
            <div>
              <p className="font-medium">Community Impact</p>
              <p className="text-sm text-muted-foreground">Supporting local community initiatives</p>
            </div>
          </div>
          <div className="flex items-center gap-3 pb-2 border-b">
            <Clock className="h-5 w-5 text-blue-500" />
            <div>
              <p className="font-medium">{mockActivityDetails.hoursAwarded} Hours Credited</p>
              <p className="text-sm text-muted-foreground">Contribution hours toward annual goal</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Users className="h-5 w-5 text-green-500" />
            <div>
              <p className="font-medium">Networking Opportunity</p>
              <p className="text-sm text-muted-foreground">Connect with fellow members</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Participants Check-in */}
      <Card>
        <CardHeader>
          <CardTitle>Participant Check-in</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {mockActivityDetails.participantList.map((participant) => (
              <div key={participant.id} className="flex items-center justify-between pb-3 border-b last:border-0">
                <div>
                  <p className="font-medium">{participant.name}</p>
                  <p className="text-xs text-muted-foreground font-mono">
                    {participant.membershipNumber}
                  </p>
                </div>
                <Button size="sm" variant={participant.checkedIn ? "default" : "outline"}>
                  {participant.checkedIn ? "✓ Checked In" : "Check In"}
                </Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
