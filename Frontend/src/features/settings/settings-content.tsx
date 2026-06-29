"use client"

import React from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Moon, Sun } from "lucide-react"
import { useTheme } from "next-themes"

export function SettingsContent() {
  const { theme, setTheme } = useTheme()

  return (
    <div className="space-y-8 max-w-2xl">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground mt-2">Manage your application preferences</p>
      </div>

      {/* Theme Settings */}
      <Card>
        <CardHeader>
          <CardTitle>Theme</CardTitle>
          <CardDescription>Choose your preferred theme</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <Button
              variant={theme === "light" ? "default" : "outline"}
              className="w-full"
              onClick={() => setTheme("light")}
            >
              <Sun className="mr-2 h-4 w-4" />
              Light
            </Button>
            <Button
              variant={theme === "dark" ? "default" : "outline"}
              className="w-full"
              onClick={() => setTheme("dark")}
            >
              <Moon className="mr-2 h-4 w-4" />
              Dark
            </Button>
            <Button
              variant={theme === "system" ? "default" : "outline"}
              className="w-full"
              onClick={() => setTheme("system")}
            >
              🖥️ System
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Notification Settings */}
      <Card>
        <CardHeader>
          <CardTitle>Notifications</CardTitle>
          <CardDescription>Manage your notification preferences</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between pb-2 border-b">
            <span className="text-sm font-medium">Email Notifications</span>
            <Badge variant="secondary">Enabled</Badge>
          </div>
          <div className="flex items-center justify-between pb-2 border-b">
            <span className="text-sm font-medium">Meeting Reminders</span>
            <Badge variant="secondary">Enabled</Badge>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Activity Updates</span>
            <Badge variant="secondary">Enabled</Badge>
          </div>
        </CardContent>
      </Card>

      {/* Privacy Settings */}
      <Card>
        <CardHeader>
          <CardTitle>Privacy</CardTitle>
          <CardDescription>Control your privacy settings</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <Button variant="outline" className="w-full">
            Manage Data & Privacy
          </Button>
          <Button variant="outline" className="w-full">
            Download Your Data
          </Button>
          <Button variant="outline" className="w-full">
            Request Account Deletion
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}