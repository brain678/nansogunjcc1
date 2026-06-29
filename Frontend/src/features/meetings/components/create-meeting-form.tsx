"use client"

import React, { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"

const createMeetingSchema = z.object({
  title: z.string().min(5, "Title must be at least 5 characters"),
  date: z.string().min(1, "Date is required"),
  time: z.string().min(1, "Time is required"),
  location: z.string().min(5, "Location is required"),
  description: z.string().min(10, "Description must be at least 10 characters"),
  maxAttendees: z.number().min(1, "Max attendees must be at least 1"),
  agenda: z.string().min(10, "Agenda is required"),
})

type CreateMeetingFormData = z.infer<typeof createMeetingSchema>

export function CreateMeetingForm() {
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<CreateMeetingFormData>({
    resolver: zodResolver(createMeetingSchema),
  })

  const onSubmit = async (data: CreateMeetingFormData) => {
    try {
      // API call would go here
      setMessage({ type: "success", text: "Meeting created successfully!" })
      reset()
      setTimeout(() => setMessage(null), 3000)
    } catch (err) {
      setMessage({ type: "error", text: "Failed to create meeting" })
    }
  }

  return (
    <div className="space-y-8 max-w-2xl">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Create New Meeting</h1>
        <p className="text-muted-foreground mt-2">Schedule an organization meeting</p>
      </div>

      {message && (
        <div
          className={`p-3 rounded-md text-sm ${
            message.type === "success"
              ? "bg-green-50 text-green-800 dark:bg-green-900/20 dark:text-green-200"
              : "bg-destructive/10 text-destructive"
          }`}
        >
          {message.text}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Meeting Details</CardTitle>
          <CardDescription>Enter meeting information</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Title */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Meeting Title</label>
              <Input {...register("title")} placeholder="e.g., Monthly General Meeting" />
              {errors.title && (
                <p className="text-xs text-destructive">{errors.title.message}</p>
              )}
            </div>

            {/* Date & Time */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Date</label>
                <Input type="date" {...register("date")} />
                {errors.date && (
                  <p className="text-xs text-destructive">{errors.date.message}</p>
                )}
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Time</label>
                <Input type="time" {...register("time")} />
                {errors.time && (
                  <p className="text-xs text-destructive">{errors.time.message}</p>
                )}
              </div>
            </div>

            {/* Location */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Location</label>
              <Input {...register("location")} placeholder="Meeting venue or 'Virtual'" />
              {errors.location && (
                <p className="text-xs text-destructive">{errors.location.message}</p>
              )}
            </div>

            {/* Description */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Description</label>
              <Textarea
                {...register("description")}
                placeholder="Meeting overview and purpose..."
                rows={4}
              />
              {errors.description && (
                <p className="text-xs text-destructive">{errors.description.message}</p>
              )}
            </div>

            {/* Agenda */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Agenda</label>
              <Textarea
                {...register("agenda")}
                placeholder="List meeting agenda items (one per line)"
                rows={4}
              />
              {errors.agenda && (
                <p className="text-xs text-destructive">{errors.agenda.message}</p>
              )}
            </div>

            {/* Max Attendees */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Maximum Attendees</label>
              <Input
                type="number"
                {...register("maxAttendees", { valueAsNumber: true })}
                placeholder="100"
              />
              {errors.maxAttendees && (
                <p className="text-xs text-destructive">{errors.maxAttendees.message}</p>
              )}
            </div>

            {/* Submit */}
            <div className="flex gap-2 pt-4">
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? "Creating..." : "Create Meeting"}
              </Button>
              <Button type="button" variant="outline" onClick={() => reset()}>
                Clear Form
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
