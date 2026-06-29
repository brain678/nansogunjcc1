"use client"

import React from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Search, Download } from "lucide-react"

const mockAuditLogs = [
  {
    id: "1",
    timestamp: new Date(Date.now() - 1 * 60 * 60 * 1000),
    user: "John Admin",
    action: "Member Approved",
    resource: "Member ID: MEM001",
    status: "success",
  },
  {
    id: "2",
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
    user: "Sarah Secretary",
    action: "Meeting Created",
    resource: "Monthly General Meeting",
    status: "success",
  },
  {
    id: "3",
    timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000),
    user: "Michael Chairman",
    action: "Member Suspended",
    resource: "Member ID: MEM045",
    status: "success",
  },
  {
    id: "4",
    timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000),
    user: "Jane Admin",
    action: "Failed Login Attempt",
    resource: "User ID: USR023",
    status: "warning",
  },
  {
    id: "5",
    timestamp: new Date(Date.now() - 8 * 60 * 60 * 1000),
    user: "John Admin",
    action: "System Settings Updated",
    resource: "Notification Settings",
    status: "success",
  },
]

export function AuditLogs() {
  const [searchTerm, setSearchTerm] = React.useState("")

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Audit Logs</h1>
          <p className="text-muted-foreground mt-2">System activity and administrative actions</p>
        </div>
        <Button variant="outline">
          <Download className="mr-2 h-4 w-4" />
          Export Logs
        </Button>
      </div>

      {/* Search & Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Search & Filter</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by user, action, or resource..."
                className="pl-10"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <Button variant="outline">Filter</Button>
          </div>
        </CardContent>
      </Card>

      {/* Audit Log Entries */}
      <div className="space-y-3">
        {mockAuditLogs.map((log) => (
          <Card key={log.id}>
            <CardContent className="pt-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="font-semibold">{log.action}</h3>
                    <Badge
                      variant={log.status === "success" ? "success" : "warning"}
                      className="text-xs"
                    >
                      {log.status === "success" ? "✓" : "⚠"} {log.status}
                    </Badge>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-muted-foreground">
                    <div>
                      <p className="text-xs uppercase">User</p>
                      <p className="font-medium text-foreground">{log.user}</p>
                    </div>
                    <div>
                      <p className="text-xs uppercase">Resource</p>
                      <p className="font-medium text-foreground">{log.resource}</p>
                    </div>
                    <div>
                      <p className="text-xs uppercase">Time</p>
                      <p className="font-medium text-foreground">
                        {log.timestamp.toLocaleTimeString()} • {log.timestamp.toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
