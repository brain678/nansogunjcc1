"use client"

import React, { useState, useEffect, useRef } from "react"
import { useSearchParams } from "next/navigation"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { useAuthStore } from "@/store/auth"
import { useRegisterMember, useResubmitMember } from "@/hooks/use-members"
import { authService } from "@/services/auth"
import { memberService } from "@/services/members"
import { documentService } from "@/services/index"
import { errorUtils } from "@/lib/utils"
import type { Member } from "@/types"

const createMemberSchema = z.object({
  firstName: z.string().min(2, "First name must be at least 2 characters"),
  lastName: z.string().min(2, "Last name must be at least 2 characters"),
  email: z.string().email("Invalid email address"),
  dateOfBirth: z.string().optional(),
  phone: z
    .string()
    .trim()
    .optional()
    .transform((value) => (value ? value : undefined))
    .refine((value) => !value || value.replace(/\D/g, "").length >= 10, {
      message: "Phone number must be at least 10 digits",
    }),
  address: z.string().min(5, "Address is required"),
  membershipType: z.enum(["full", "associate", "honorary", "student"]),
  notes: z.string().optional(),
})

type CreateMemberFormData = z.infer<typeof createMemberSchema>

export function CreateMemberForm() {
  const currentUser = useAuthStore((state) => state.user)
  const tokens = useAuthStore((state) => state.tokens)
  const hasHydrated = useAuthStore((state) => state.hasHydrated)
  const searchParams = useSearchParams()
  const isResubmissionMode = searchParams.get("mode") === "resubmit"
  const memberId = searchParams.get("memberId") || ""
  const hasAuthToken = Boolean(tokens?.accessToken)
  const createMemberMutation = useRegisterMember()
  const resubmitMemberMutation = useResubmitMember()
  const isPending = (createMemberMutation as any).isPending || (resubmitMemberMutation as any).isPending
  const [passportPhoto, setPassportPhoto] = useState<File | null>(null)
  const [passportPhotoPreview, setPassportPhotoPreview] = useState<string | null>(null)
  const [studentIdCard, setStudentIdCard] = useState<File | null>(null)
  const [studentIdCardPreview, setStudentIdCardPreview] = useState<string | null>(null)
  const [submittedMember, setSubmittedMember] = useState<Member | null>(null)
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null)
  const [isLoadingResubmissionData, setIsLoadingResubmissionData] = useState(false)
  const [resubmissionMemberRecordId, setResubmissionMemberRecordId] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    trigger,
    watch,
    getValues,
    formState: { errors },
    reset,
  } = useForm<CreateMemberFormData>({
    resolver: zodResolver(createMemberSchema),
    defaultValues: {
      firstName: currentUser?.firstName || "",
      lastName: currentUser?.lastName || "",
      email: currentUser?.email || "",
      phone: currentUser?.phone || "",
      address: "",
      membershipType: "full",
      notes: "",
      dateOfBirth: "",
    },
  })

  const watchMembershipType = watch("membershipType")
  const watchAddress = watch("address")
  const watchNotes = watch("notes")
  const watchFirstName = watch("firstName")
  const watchLastName = watch("lastName")
  const watchEmail = watch("email")
  const watchPhone = watch("phone")
  const watchDateOfBirth = watch("dateOfBirth")

  const [step, setStep] = useState(1)
  const autoSubmitTriggeredRef = useRef(false)

  const normalizeMembershipType = (type?: string): "full" | "associate" | "honorary" | "student" => {
    switch (type) {
      case "individual":
        return "full"
      case "corporate":
        return "associate"
      case "student":
      case "full":
      case "associate":
      case "honorary":
        return type
      default:
        return "full"
    }
  }

  const stepFields = (currentStep: number) => {
    if (currentStep === 1) {
      return ["membershipType", "address", "notes"] as const
    }
    return [] as const
  }

  const nextStep = async () => {
    if (step === 1) {
      const valid = await trigger(stepFields(1))
      if (!valid) {
        return
      }
    }

    if (step === 2 && !passportPhoto) {
      setMessage({ type: "error", text: "Please upload your passport photo before continuing." })
      return
    }

    if (step === 3 && !studentIdCard) {
      setMessage({ type: "error", text: "Please upload your student ID before continuing." })
      return
    }

    setMessage(null)
    setStep((current) => Math.min(current + 1, 4))
  }

  const prevStep = () => {
    setStep((current) => Math.max(current - 1, 1))
  }

  useEffect(() => {
    if (!passportPhoto) {
      setPassportPhotoPreview(null)
      return
    }

    const objectUrl = URL.createObjectURL(passportPhoto)
    setPassportPhotoPreview(objectUrl)

    return () => {
      URL.revokeObjectURL(objectUrl)
    }
  }, [passportPhoto])

  useEffect(() => {
    if (!studentIdCard || !studentIdCard.type.startsWith("image/")) {
      setStudentIdCardPreview(null)
      return
    }

    const objectUrl = URL.createObjectURL(studentIdCard)
    setStudentIdCardPreview(objectUrl)

    return () => {
      URL.revokeObjectURL(objectUrl)
    }
  }, [studentIdCard])

  const clearPassportPhoto = () => setPassportPhoto(null)
  const clearStudentIdCard = () => setStudentIdCard(null)

  const handleFormSubmit = React.useCallback(async (data: CreateMemberFormData) => {
    try {
      if (isResubmissionMode && (!hasHydrated || !hasAuthToken)) {
        setMessage({ type: "error", text: "Please sign in again before resubmitting your application." })
        return
      }

      if (isResubmissionMode && memberId) {
        if (passportPhoto) {
          try {
            await authService.uploadProfilePhoto(passportPhoto)
          } catch (err) {
            console.warn("Failed to upload passport photo")
          }
        }

        if (studentIdCard) {
          try {
            await documentService.upload(studentIdCard, "student_id_card")
          } catch (err) {
            console.warn("Failed to upload student ID")
          }
        }

        const result = await resubmitMemberMutation.mutateAsync({
          id: memberId,
          memberRecordId: resubmissionMemberRecordId || undefined,
          email: data.email,
          firstName: data.firstName,
          lastName: data.lastName,
          phone: data.phone,
          address: data.address,
          notes: data.notes,
          dateOfBirth: data.dateOfBirth,
          membershipType: data.membershipType,
          membershipTier: "standard",
          expiryMonths: 12,
          comment: "Resubmitted application",
        })
        setSubmittedMember(result.member)
        setMessage({ type: "success", text: "Your resubmission has been received and will be reviewed again." })
      } else {
        const member = await createMemberMutation.mutateAsync(data as any)
        setSubmittedMember(member)

        if (passportPhoto) {
          try {
            await authService.uploadProfilePhoto(passportPhoto)
          } catch (err) {
            console.warn("Failed to upload passport photo")
          }
        }

        if (studentIdCard) {
          try {
            await documentService.upload(studentIdCard, "student_id_card")
          } catch (err) {
            console.warn("Failed to upload student ID")
          }
        }

        setMessage({ type: "success", text: "Membership application submitted successfully!" })
      }
      reset({
        firstName: currentUser?.firstName || "",
        lastName: currentUser?.lastName || "",
        email: currentUser?.email || "",
        phone: currentUser?.phone || "",
        address: "",
        membershipType: "full",
        notes: "",
        dateOfBirth: "",
      })
      localStorage.removeItem("pendingMembershipData")
      setTimeout(() => setMessage(null), 3000)
    } catch (err) {
      setMessage({
        type: "error",
        text: errorUtils.getErrorMessage(err) || "Failed to submit membership application",
      })
      throw err
    }
  }, [createMemberMutation, resubmitMemberMutation, passportPhoto, studentIdCard, currentUser, reset, isResubmissionMode, memberId, hasHydrated, hasAuthToken])

  const progressPercent = ((step - 1) / 3) * 100

  useEffect(() => {
    if (isResubmissionMode) return
    if (step !== 4 || submittedMember || isPending || autoSubmitTriggeredRef.current) return

    autoSubmitTriggeredRef.current = true
    void handleFormSubmit(getValues())
  }, [step, submittedMember, isPending, getValues, handleFormSubmit, isResubmissionMode])

  useEffect(() => {
    if (step !== 4) {
      autoSubmitTriggeredRef.current = false
    }
  }, [step])

  useEffect(() => {
    if (!isResubmissionMode || !memberId) return

    let isMounted = true
    setIsLoadingResubmissionData(true)

    const loadResubmissionData = async () => {
      try {
        let existingMember: Member | null = null

        try {
          existingMember = await memberService.getByUserId(memberId)
        } catch {
          try {
            existingMember = await memberService.getById(memberId)
          } catch {
            existingMember = null
          }
        }

        if (!existingMember) {
          if (isMounted) {
            reset({
              firstName: currentUser?.firstName || "",
              lastName: currentUser?.lastName || "",
              email: currentUser?.email || "",
              phone: currentUser?.phone || "",
              address: "",
              membershipType: "full",
              notes: "",
              dateOfBirth: "",
            })
            setResubmissionMemberRecordId(null)
          }
          return
        }

        if (!isMounted) return

        setResubmissionMemberRecordId(existingMember.id)

        reset({
          firstName: existingMember.firstName || currentUser?.firstName || "",
          lastName: existingMember.lastName || currentUser?.lastName || "",
          email: existingMember.email || currentUser?.email || "",
          phone: existingMember.phone || currentUser?.phone || "",
          address: existingMember.address || "",
          membershipType: normalizeMembershipType(existingMember.membershipType),
          notes: existingMember.notes || "",
          dateOfBirth: existingMember.dateOfBirth || "",
        })
      } finally {
        if (isMounted) {
          setIsLoadingResubmissionData(false)
        }
      }
    }

    void loadResubmissionData()

    return () => {
      isMounted = false
    }
  }, [isResubmissionMode, memberId, currentUser, reset])

  useEffect(() => {
    if (typeof window === "undefined") return
    if (isResubmissionMode) return
    const raw = localStorage.getItem("pendingMembershipData")
    const persistedData = raw ? JSON.parse(raw) : {}

    reset({
      firstName: currentUser?.firstName || persistedData.firstName || "",
      lastName: currentUser?.lastName || persistedData.lastName || "",
      email: currentUser?.email || persistedData.email || "",
      phone: currentUser?.phone || persistedData.phone || "",
      address: persistedData.address || "",
      membershipType: normalizeMembershipType(persistedData.membershipType),
      notes: persistedData.notes || "",
      dateOfBirth: persistedData.dateOfBirth || "",
    })
  }, [currentUser, reset, isResubmissionMode])

  return (
    <div className="space-y-8 max-w-2xl">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">
          {isResubmissionMode ? "Resubmit Your Membership Application" : "Complete Your Membership Application"}
        </h1>
        <p className="text-muted-foreground mt-2">
          {isResubmissionMode
            ? "Your last application was rejected. Update your details and re-upload the documents below so the review can continue."
            : "We already have your account details. Please complete the membership-specific information below."}
        </p>
      </div>

      {message && (
        <div
          className={`p-3 rounded-md text-sm ${
            message.type === "success"
              ? "bg-[#E8F7F1] text-[#006f45]"
              : "bg-[#FDECEC] text-[#B42318]"
          }`}
        >
          {message.text}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Membership Application</CardTitle>
          <CardDescription>Step through a guided membership registration flow.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="mb-6 space-y-4">
            <div className="flex items-center justify-between gap-2">
              {[
                { title: "Membership", step: 1 },
                { title: "Passport", step: 2 },
                { title: "Student ID", step: 3 },
                { title: "Review", step: 4 },
              ].map((item) => (
                <div key={item.step} className="text-center flex-1">
                  <div
                    className={`mx-auto mb-2 flex h-9 w-9 items-center justify-center rounded-full border text-sm font-semibold ${
                      step === item.step ? "border-[#008753] bg-[#008753] text-white" : "border-[#008753]/20 bg-white text-[#4B5F54]"
                    }`}>
                    {item.step}
                  </div>
                  <p className="text-xs uppercase tracking-[0.15em] text-muted-foreground">{item.title}</p>
                </div>
              ))}
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-[#E8F7F1]">
              <div className="h-full rounded-full bg-[#008753]" style={{ width: `${progressPercent}%` }} />
            </div>
          </div>

          <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
            {currentUser ? (
              <div className="rounded-2xl border border-[#008753]/15 bg-[#F5F7F5] p-5">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <p className="text-sm font-semibold text-slate-900">Account details already on file</p>
                    <p className="text-sm text-slate-600">These values are pulled from your registered account.</p>
                  </div>
                  <Badge variant="secondary">Verified</Badge>
                </div>

                <div className="mt-5 grid gap-4 sm:grid-cols-2">
                  <div className="rounded-xl bg-white p-4 shadow-sm border border-slate-200">
                    <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Name</p>
                    <p className="mt-2 text-sm font-medium text-slate-900">{currentUser.firstName} {currentUser.lastName}</p>
                  </div>
                  <div className="rounded-xl bg-white p-4 shadow-sm border border-slate-200">
                    <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Email</p>
                    <p className="mt-2 text-sm font-medium text-slate-900">{currentUser.email}</p>
                  </div>
                  <div className="rounded-xl bg-white p-4 shadow-sm border border-slate-200 sm:col-span-2">
                    <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Phone</p>
                    <p className="mt-2 text-sm font-medium text-slate-900">{currentUser.phone || "Not provided"}</p>
                  </div>
                </div>
              </div>
            ) : null}

            {isResubmissionMode ? (
              <div className="space-y-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="space-y-1">
                  <p className="text-base font-semibold text-slate-900">Edit your application details</p>
                  <p className="text-sm text-slate-500">Update any field below before submitting your resubmission.</p>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-[#1E302A]">First name</label>
                    <input
                      className="w-full rounded-md border border-input bg-background px-3 py-3 text-sm text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#008753] focus-visible:ring-offset-2"
                      {...register("firstName")}
                    />
                    {errors.firstName && <p className="text-xs text-destructive">{errors.firstName.message}</p>}
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium text-[#1E302A]">Last name</label>
                    <input
                      className="w-full rounded-md border border-input bg-background px-3 py-3 text-sm text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#008753] focus-visible:ring-offset-2"
                      {...register("lastName")}
                    />
                    {errors.lastName && <p className="text-xs text-destructive">{errors.lastName.message}</p>}
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium text-[#1E302A]">Email</label>
                    <input
                      type="email"
                      className="w-full rounded-md border border-input bg-background px-3 py-3 text-sm text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#008753] focus-visible:ring-offset-2"
                      {...register("email")}
                    />
                    {errors.email && <p className="text-xs text-destructive">{errors.email.message}</p>}
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium text-[#1E302A]">Phone</label>
                    <input
                      type="tel"
                      className="w-full rounded-md border border-input bg-background px-3 py-3 text-sm text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#008753] focus-visible:ring-offset-2"
                      {...register("phone")}
                    />
                    {errors.phone && <p className="text-xs text-destructive">{errors.phone.message}</p>}
                  </div>

                  <div className="space-y-2 md:col-span-2">
                    <label className="text-sm font-medium text-[#1E302A]">Date of birth</label>
                    <input
                      type="date"
                      className="w-full rounded-md border border-input bg-background px-3 py-3 text-sm text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#008753] focus-visible:ring-offset-2"
                      {...register("dateOfBirth")}
                    />
                    {errors.dateOfBirth && <p className="text-xs text-destructive">{errors.dateOfBirth.message}</p>}
                  </div>
                </div>
              </div>
            ) : (
              <>
                <input type="hidden" {...register("firstName")} />
                <input type="hidden" {...register("lastName")} />
                <input type="hidden" {...register("email")} />
                <input type="hidden" {...register("phone")} />
                <input type="hidden" {...register("dateOfBirth")} />
              </>
            )}

            {step === 1 && (
              <div className="space-y-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="space-y-1">
                  <p className="text-base font-semibold text-slate-900">Choose membership type</p>
                  <p className="text-sm text-slate-500">Pick the option that best fits your participation with NANS.</p>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-[#1E302A]">Membership type</label>
                  <select
                    className="w-full rounded-md border border-input bg-background px-3 py-3 text-sm text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#008753] focus-visible:ring-offset-2"
                    {...register("membershipType")}
                  >
                    <option value="full">Full membership</option>
                    <option value="associate">Associate membership</option>
                    <option value="honorary">Honorary membership</option>
                    <option value="student">Student membership</option>
                  </select>
                  {errors.membershipType && (
                    <p className="text-xs text-destructive">{errors.membershipType.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-[#1E302A]">Address</label>
                  <Textarea
                    {...register("address")}
                    className="text-foreground"
                    placeholder="Enter your address for membership verification"
                    rows={4}
                  />
                  {errors.address && (
                    <p className="text-xs text-destructive">{errors.address.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-[#1E302A]">Additional information</label>
                  <Textarea
                    {...register("notes")}
                    className="text-foreground"
                    placeholder="Share anything important for your membership review"
                    rows={4}
                  />
                  {errors.notes && (
                    <p className="text-xs text-destructive">{errors.notes.message}</p>
                  )}
                </div>
              </div>
            )}

            {step === 2 && (
              <div className="space-y-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="space-y-1">
                  <p className="text-base font-semibold text-slate-900">Passport upload</p>
                  <p className="text-sm text-slate-500">Upload your passport or profile photo for identity verification.</p>
                </div>

                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                  <label className="block text-sm font-semibold text-slate-900 mb-3">Passport / Profile Photo</label>
                  <div className="flex flex-col gap-3">
                    <label className="group flex cursor-pointer items-center justify-between rounded-xl border border-dashed border-slate-300 bg-white p-4 text-sm text-slate-700 transition hover:border-slate-400">
                      <span>{passportPhoto?.name || "Choose passport photo"}</span>
                      <span className="rounded-full border border-slate-300 bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700 transition group-hover:bg-slate-200">Browse</span>
                      <input
                        type="file"
                        accept="image/*"
                        className="sr-only"
                        disabled={isPending}
                        onChange={(e) => setPassportPhoto(e.target.files ? e.target.files[0] : null)}
                      />
                    </label>
                    {passportPhoto && !isPending ? (
                      <div className="flex items-center justify-between gap-3 rounded-xl border border-slate-200 bg-white p-3">
                        <div>
                          <p className="text-xs font-semibold text-slate-600">Selected</p>
                          <p className="mt-1 text-sm text-slate-700">{passportPhoto.name}</p>
                        </div>
                        <Button type="button" variant="outline" size="sm" onClick={clearPassportPhoto}>
                          Remove
                        </Button>
                      </div>
                    ) : null}
                    {passportPhotoPreview ? (
                      <div className="mt-3 rounded-xl border border-slate-200 bg-white p-3">
                        <p className="text-xs font-semibold text-slate-600">Preview</p>
                        <img
                          src={passportPhotoPreview}
                          alt="Passport preview"
                          className="mt-2 h-40 w-full rounded-md object-cover"
                        />
                      </div>
                    ) : (
                      <p className="mt-2 text-xs text-slate-500">Accepted formats: JPG, PNG. Max file size depends on your browser.</p>
                    )}
                  </div>
                </div>
              </div>
            )}

            {step === 3 && (
              <div className="space-y-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="space-y-1">
                  <p className="text-base font-semibold text-slate-900">Student ID upload</p>
                  <p className="text-sm text-slate-500">Upload your student ID card or supporting document.</p>
                </div>

                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                  <label className="block text-sm font-semibold text-slate-900 mb-3">Student ID / Supporting Document</label>
                  <div className="flex flex-col gap-3">
                    <label className="group flex cursor-pointer items-center justify-between rounded-xl border border-dashed border-slate-300 bg-white p-4 text-sm text-slate-700 transition hover:border-slate-400">
                      <span>{studentIdCard?.name || "Choose student ID"}</span>
                      <span className="rounded-full border border-slate-300 bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700 transition group-hover:bg-slate-200">Browse</span>
                      <input
                        type="file"
                        accept="image/*,application/pdf"
                        className="sr-only"
                        disabled={isPending}
                        onChange={(e) => setStudentIdCard(e.target.files ? e.target.files[0] : null)}
                      />
                    </label>
                    {studentIdCard && !isPending ? (
                      <div className="flex items-center justify-between gap-3 rounded-xl border border-slate-200 bg-white p-3">
                        <div>
                          <p className="text-xs font-semibold text-slate-600">Selected</p>
                          <p className="mt-1 text-sm text-slate-700">{studentIdCard.name}</p>
                        </div>
                        <Button type="button" variant="outline" size="sm" onClick={clearStudentIdCard}>
                          Remove
                        </Button>
                      </div>
                    ) : null}
                    {studentIdCardPreview ? (
                      <div className="mt-3 rounded-xl border border-slate-200 bg-white p-3">
                        <p className="text-xs font-semibold text-slate-600">Preview</p>
                        <img
                          src={studentIdCardPreview}
                          alt="Student ID preview"
                          className="mt-2 h-40 w-full rounded-md object-cover"
                        />
                      </div>
                    ) : (
                      <p className="mt-2 text-xs text-slate-500">You can also upload a PDF. If a PDF is selected, it will be stored without an image preview.</p>
                    )}
                  </div>
                </div>
              </div>
            )}

            {step === 4 && (
              <div className="space-y-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div className="space-y-1">
                    <p className="text-base font-semibold text-slate-900">Review your application</p>
                    <p className="text-sm text-slate-500">Everything below is ready to be sent. You can still go back and adjust anything before it is finalized.</p>
                  </div>
                  <Badge variant={submittedMember ? "default" : "secondary"}>
                    {submittedMember ? "Submitted" : "Pending submission"}
                  </Badge>
                </div>

                <div className="grid gap-4 lg:grid-cols-2">
                  <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                    <p className="text-sm font-semibold text-slate-900">Account details</p>
                    <div className="mt-3 space-y-3 text-sm text-slate-700">
                      <div>
                        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Full name</p>
                        <p className="mt-1 font-medium text-slate-900">{watchFirstName || currentUser?.firstName || "Not provided"} {watchLastName || currentUser?.lastName || ""}</p>
                      </div>
                      <div>
                        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Email</p>
                        <p className="mt-1 font-medium text-slate-900">{watchEmail || currentUser?.email || "Not provided"}</p>
                      </div>
                      <div>
                        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Phone</p>
                        <p className="mt-1 font-medium text-slate-900">{watchPhone || currentUser?.phone || "Not provided"}</p>
                      </div>
                      <div>
                        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Date of birth</p>
                        <p className="mt-1 font-medium text-slate-900">{watchDateOfBirth || "Not provided"}</p>
                      </div>
                    </div>
                  </div>

                  <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                    <p className="text-sm font-semibold text-slate-900">Membership request</p>
                    <div className="mt-3 space-y-3 text-sm text-slate-700">
                      <div>
                        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Membership type</p>
                        <p className="mt-1 font-medium text-slate-900">{watchMembershipType || "Full membership"}</p>
                      </div>
                      <div>
                        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Address</p>
                        <p className="mt-1 font-medium text-slate-900">{watchAddress || "Not provided"}</p>
                      </div>
                      <div>
                        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Additional notes</p>
                        <p className="mt-1 font-medium text-slate-900">{watchNotes || "No additional notes provided"}</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                  <p className="text-sm font-semibold text-slate-900">Documents uploaded</p>
                  <div className="mt-3 grid gap-3 sm:grid-cols-2">
                    <div className="rounded-xl border border-slate-200 bg-white p-3">
                      <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Passport / profile photo</p>
                      <p className="mt-1 text-sm font-medium text-slate-900">{passportPhoto?.name || "Not uploaded"}</p>
                    </div>
                    <div className="rounded-xl border border-slate-200 bg-white p-3">
                      <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Student ID / document</p>
                      <p className="mt-1 text-sm font-medium text-slate-900">{studentIdCard?.name || "Not uploaded"}</p>
                    </div>
                  </div>
                </div>

                {submittedMember ? (
                  <div className="rounded-2xl border border-[#008753]/20 bg-[#E8F7F1] p-4 text-sm text-[#006f45]">
                    <p className="font-semibold">Application submitted successfully</p>
                    <p className="mt-2">Your membership request has been received and is now awaiting review.</p>
                    <div className="mt-3 grid gap-3 sm:grid-cols-2">
                      <div>
                        <p className="text-xs uppercase tracking-[0.2em] text-green-700">Status</p>
                        <p className="mt-1 font-medium">{submittedMember.status}</p>
                      </div>
                      <div>
                        <p className="text-xs uppercase tracking-[0.2em] text-green-700">Membership number</p>
                        <p className="mt-1 font-medium">{submittedMember.membershipNumber || "Pending assignment"}</p>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="rounded-2xl border border-[#008753]/10 bg-[#F5F7F5] p-4 text-sm text-slate-600">
                    <p className="font-semibold text-slate-900">Almost done</p>
                    <p className="mt-1">Your application is being submitted right after this review page appears. You can still use the Back button to make changes before it is finalized.</p>
                  </div>
                )}
              </div>
            )}

            <div className="flex items-center justify-between gap-3">
              <Button type="button" variant="outline" onClick={prevStep} disabled={step === 1 || isPending}>
                {step === 4 ? "Edit details" : "Back"}
              </Button>
              {step < 4 ? (
                <Button
                  type="button"
                  onClick={nextStep}
                  disabled={
                    isPending ||
                    (step === 2 && !passportPhoto) ||
                    (step === 3 && !studentIdCard)
                  }
                >
                  Continue
                </Button>
              ) : isResubmissionMode ? (
                <Button
                  type="submit"
                  disabled={isPending || !hasHydrated || !hasAuthToken || isLoadingResubmissionData}
                  className="min-w-[180px]"
                >
                  {isPending ? "Submitting your resubmission..." : isLoadingResubmissionData ? "Loading application..." : "Submit resubmission"}
                </Button>
              ) : (
                <span className="text-sm text-slate-500">
                  {isPending ? "Submitting your application..." : submittedMember ? "Application submitted" : "Ready to submit"}
                </span>
              )}
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
