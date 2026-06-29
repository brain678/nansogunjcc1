"use client"

import React, { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"

const createActivitySchema = z.object({
  title: z.string().min(5, "Title must be at least 5 characters"),
  date: z.string().min(1, "Date is required"),
  time: z.string().min(1, "Time is required"),
  location: z.string().min(5, "Location is required"),
  description: z.string().min(10, "Description must be at least 10 characters"),
  category: z.enum(["community-service", "education", "social", "fundraiser", "networking"]),
  hoursAwarded: z.number().min(0, "Hours must be 0 or more"),
  maxParticipants: z.number().min(1, "Max participants must be at least 1"),
})

type CreateActivityFormData = z.infer<typeof createActivitySchema>

export function CreateActivityForm() {
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<CreateActivityFormData>({
    resolver: zodResolver(createActivitySchema),
  })

  const onSubmit = async (data: CreateActivityFormData) => {
    try {
      // API call would go here
      setMessage({ type: "success", text: "Activity created successfully!" })
      reset()
      setTimeout(() => setMessage(null), 3000)
    } catch (err) {
      setMessage({ type: "error", text: "Failed to create activity" })
    }
  }

  return (
    <div className="space-y-8 max-w-2xl">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Create New Activity</h1>
        <p className="text-muted-foreground mt-2">Organize a new member activity</p>
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
          <CardTitle>Activity Details</CardTitle>
          <CardDescription>Enter activity information</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Title */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Activity Title</label>
              <Input {...register("title")} placeholder="e.g., Community Cleanup Drive" />
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
              <Input {...register("location")} placeholder="Activity venue" />
              {errors.location && (
                <p className="text-xs text-destructive">{errors.location.message}</p>
              )}
            </div>

            {/* Category */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Category</label>
              <select
                {...register("category")}
                className="w-full px-3 py-2 border rounded-md bg-background"
              >
                <option value="">Select a category</option>
                <option value="community-service">Community Service</option>
                <option value="education">Education</option>
                <option value="social">Social</option>
                <option value="fundraiser">Fundraiser</option>
                <option value="networking">Networking</option>
              </select>
              {errors.category && (
                <p className="text-xs text-destructive">{errors.category.message}</p>
              )}
            </div>

            {/* Description */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Description</label>
              <Textarea
                {...register("description")}
                placeholder="Activity overview and details..."
                rows={4}
              />
              {errors.description && (
                <p className="text-xs text-destructive">{errors.description.message}</p>
              )}
            </div>

            {/* Hours & Participants */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Hours Awarded</label>
                <Input
                  type="number"
                  step="0.5"
                  {...register("hoursAwarded", { valueAsNumber: true })}
                  placeholder="2"
                />
                {errors.hoursAwarded && (
                  <p className="text-xs text-destructive">{errors.hoursAwarded.message}</p>
                )}
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Max Participants</label>
                <Input
                  type="number"
                  {...register("maxParticipants", { valueAsNumber: true })}
                  placeholder="50"
                />
                {errors.maxParticipants && (
                  <p className="text-xs text-destructive">{errors.maxParticipants.message}</p>
                )}
              </div>
            </div>

            {/* Submit */}
            <div className="flex gap-2 pt-4">
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? "Creating..." : "Create Activity"}
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
