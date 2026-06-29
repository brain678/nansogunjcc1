"use client"

import React from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Calendar, Users, MapPin, Plus } from "lucide-react"
import Link from "next/link"

const mockActivities = [
  {
    id: "1",
    title: "Community Cleanup Drive",
    date: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000),
    location: "Central Park",
    participants: 32,
    status: "upcoming",
  },
  {
    id: "2",
    title: "Education Workshop",
    date: new Date(Date.now() + 10 * 24 * 60 * 60 * 1000),
    location: "NANS Training Center",
    participants: 28,
    status: "upcoming",
  },
  {
    id: "3",
    title: "Charity Fundraiser",
    date: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000),
    location: "Community Hall",
    participants: 50,
    status: "completed",
  },
]

export function ActivitiesList() {
  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Activities</h1>
          <p className="text-muted-foreground mt-2">View and participate in activities</p>
        </div>
        <Link href="/activities/create">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Create Activity
          </Button>
        </Link>
      </div>

      {/* Activities Cards */}
      <div className="space-y-4">
        {mockActivities.map((activity) => (
          <Card key={activity.id} className="hover:shadow-md transition-shadow">
            <CardContent className="pt-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold">{activity.title}</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4 text-sm text-muted-foreground">
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4" />
                      <span>{activity.date.toLocaleDateString()}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <MapPin className="h-4 w-4" />
                      <span>{activity.location}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Users className="h-4 w-4" />
                      <span>{activity.participants} participants</span>
                    </div>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Badge variant={activity.status === "completed" ? "secondary" : "default"}>
                    {activity.status === "completed" ? "✅ Completed" : "📅 Upcoming"}
                  </Badge>
                  <Link href={`/activities/${activity.id}`}>
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
