"use client"

import React, { useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { useRegister } from "@/hooks/use-auth"

const registerSchema = z
  .object({
    firstName: z.string().min(2),
    lastName: z.string().min(2),
    otherNames: z.string().optional(),
    gender: z.enum(["male", "female", "other"]).optional(),
    dateOfBirthMonth: z.string().optional(),
    dateOfBirthDay: z.string().optional(),
    phone: z.string().optional(),
    email: z.string().email(),
    institution: z.string().optional(),
    faculty: z.string().optional(),
    department: z.string().optional(),
    level: z.string().optional(),
    matricNumber: z.string().optional(),
    expectedGraduationYear: z.string().optional(),
    password: z
      .string()
      .min(8, "Password must be at least 8 characters")
      .regex(/[A-Z]/, "Password must contain at least one uppercase letter")
      .regex(/[a-z]/, "Password must contain at least one lowercase letter")
      .regex(/\d/, "Password must contain at least one number")
      .regex(/[!@#$%^&*()_+\-=[\]{}|;:,.<>?]/, "Password must contain at least one special character"),
    confirmPassword: z.string(),
    address: z.string().optional(),
    notes: z.string().optional(),
  })
  .refine((d) => d.password === d.confirmPassword, {
    message: "Passwords don't match",
    path: ["confirmPassword"],
  })

type RegisterFormData = z.infer<typeof registerSchema>

export function RegisterForm() {
  const router = useRouter()
  const { mutate: register, isPending } = useRegister()
  const [step, setStep] = useState(1)
  const [error, setError] = useState<string | null>(null)

  const {
    register: formRegister,
    handleSubmit,
    trigger,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      dateOfBirthMonth: "",
      dateOfBirthDay: "",
    },
    mode: "onTouched",
  })

  const stepFields = (currentStep: number) => {
    if (currentStep === 1) {
      return ["firstName", "lastName"] as const
    }
    if (currentStep === 2) {
      return ["email", "phone", "password", "confirmPassword"] as const
    }
    return [
      "otherNames",
      "gender",
      "dateOfBirthMonth",
      "dateOfBirthDay",
      "institution",
      "faculty",
      "department",
      "level",
      "matricNumber",
      "expectedGraduationYear",
      "address",
      "notes",
    ] as const
  }

  const nextStep = async () => {
    const valid = await trigger(stepFields(step) as any)
    if (valid) {
      setStep((current) => Math.min(current + 1, 3))
    }
  }

  const prevStep = () => setStep((current) => Math.max(current - 1, 1))

  const progressPercent = ((step - 1) / 2) * 100

  const onSubmit = async (data: RegisterFormData) => {
    setError(null)
    try {
      const dateOfBirth = data.dateOfBirthMonth && data.dateOfBirthDay
        ? `${data.dateOfBirthMonth.padStart(2, "0")}-${data.dateOfBirthDay.padStart(2, "0")}`
        : ""

      if (typeof window !== "undefined") {
        const pending = {
          otherNames: data.otherNames || "",
          gender: data.gender || "",
          dateOfBirth,
          institution: data.institution || "",
          faculty: data.faculty || "",
          department: data.department || "",
          level: data.level || "",
          matricNumber: data.matricNumber || "",
          expectedGraduationYear: data.expectedGraduationYear || "",
          address: data.address || "",
          notes: data.notes || "",
        }
        localStorage.setItem("pendingMembershipData", JSON.stringify(pending))
      }

      router.replace("/members/create")

      register({
        firstName: data.firstName,
        lastName: data.lastName,
        email: data.email,
        phone: data.phone,
        password: data.password,
      })
    } catch (err) {
      setError("Registration failed. Please try again.")
    }
  }

  const months = [
    { value: "01", label: "January" },
    { value: "02", label: "February" },
    { value: "03", label: "March" },
    { value: "04", label: "April" },
    { value: "05", label: "May" },
    { value: "06", label: "June" },
    { value: "07", label: "July" },
    { value: "08", label: "August" },
    { value: "09", label: "September" },
    { value: "10", label: "October" },
    { value: "11", label: "November" },
    { value: "12", label: "December" },
  ]

  return (
    <Card className="border-[#008753]/10 bg-white shadow-sm">
      <CardHeader>
        <CardTitle className="text-[#008753]">Create Account</CardTitle>
        <CardDescription>Secure sign-up and membership application flow</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="mb-6 space-y-4">
          <div className="flex items-center justify-between gap-2">
            {["Name", "Credentials", "Membership"].map((title, index) => (
              <div key={title} className="text-center flex-1">
                <div
                  className={`mx-auto mb-2 flex h-8 w-8 items-center justify-center rounded-full border text-sm font-semibold ${
                    step === index + 1 ? "border-[#008753] bg-[#008753] text-white" : "border-[#008753]/20 bg-[#F5F7F5] text-[#4B5F54]"
                  }`}>
                  {index + 1}
                </div>
                <p className="text-xs uppercase tracking-[0.15em] text-[#4B5F54]">{title}</p>
              </div>
            ))}
          </div>

          <div className="h-2 overflow-hidden rounded-full bg-[#E8F7F1]">
            <div className="h-full rounded-full bg-[#008753]" style={{ width: `${progressPercent}%` }} />
          </div>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 text-[#1E302A]">
          {error && (
            <div className="rounded-md bg-[#FDECEC] p-3 text-sm text-[#B42318]">
              {error}
            </div>
          )}

          {step === 1 && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">First Name</label>
                  <Input placeholder="John" {...formRegister("firstName")} disabled={isPending} />
                  {errors.firstName && <p className="text-xs text-destructive">{errors.firstName.message}</p>}
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Last Name</label>
                  <Input placeholder="Doe" {...formRegister("lastName")} disabled={isPending} />
                  {errors.lastName && <p className="text-xs text-destructive">{errors.lastName.message}</p>}
                </div>
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-6">
              <div className="space-y-2">
                <label className="text-sm font-medium">Email</label>
                <Input type="email" placeholder="you@email.com" {...formRegister("email")} disabled={isPending} />
                {errors.email && <p className="text-xs text-destructive">{errors.email.message}</p>}
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Phone</label>
                <Input type="tel" placeholder="Phone number" {...formRegister("phone")} disabled={isPending} />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Password</label>
                  <Input type="password" placeholder="At least 8 chars" {...formRegister("password")} disabled={isPending} />
                  {errors.password && <p className="text-xs text-destructive">{errors.password.message}</p>}
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Confirm Password</label>
                  <Input type="password" placeholder="Confirm password" {...formRegister("confirmPassword")} disabled={isPending} />
                  {errors.confirmPassword && <p className="text-xs text-destructive">{errors.confirmPassword.message}</p>}
                </div>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-[#1E302A]">Other Names</label>
                  <Input placeholder="Other names" {...formRegister("otherNames")} disabled={isPending} />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-[#1E302A]">Gender</label>
                  <select
                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#008753] focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    {...formRegister("gender") as any}
                    disabled={isPending}
                  >
                    <option value="">Prefer not to say</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-[#1E302A]">Birth Month</label>
                  <select
                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#008753] focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    {...formRegister("dateOfBirthMonth") as any}
                    disabled={isPending}
                  >
                    <option value="">Select month</option>
                    {months.map((month) => (
                      <option key={month.value} value={month.value}>
                        {month.label}
                      </option>
                    ))}
                  </select>
                  {errors.dateOfBirthMonth && <p className="text-xs text-[#B42318]">{errors.dateOfBirthMonth.message}</p>}
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-[#1E302A]">Birth Day</label>
                  <Input type="number" min="1" max="31" placeholder="Day" {...formRegister("dateOfBirthDay") as any} disabled={isPending} />
                  {errors.dateOfBirthDay && <p className="text-xs text-[#B42318]">{errors.dateOfBirthDay.message}</p>}
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-[#1E302A]">Institution / Organization</label>
                <Input placeholder="Institution" {...formRegister("institution")} disabled={isPending} />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-[#1E302A]">Faculty</label>
                  <Input placeholder="Faculty" {...formRegister("faculty")} disabled={isPending} />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-[#1E302A]">Department</label>
                  <Input placeholder="Department" {...formRegister("department")} disabled={isPending} />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-[#1E302A]">Level</label>
                  <Input placeholder="Level (e.g. 300)" {...formRegister("level")} disabled={isPending} />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-[#1E302A]">Matric Number</label>
                  <Input placeholder="Matric number" {...formRegister("matricNumber")} disabled={isPending} />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-[#1E302A]">Expected Graduation Year</label>
                  <Input placeholder="2026" {...formRegister("expectedGraduationYear")} disabled={isPending} />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-[#1E302A]">Address</label>
                  <Input placeholder="Address" {...formRegister("address")} disabled={isPending} />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-[#1E302A]">Notes (Optional)</label>
                <Textarea {...formRegister("notes")} placeholder="Additional information" rows={3} disabled={isPending} />
              </div>

            </div>
          )}

          <div className="flex items-center justify-between gap-3">
            <Button type="button" variant="outline" onClick={prevStep} disabled={step === 1 || isPending}>
              Back
            </Button>
            {step < 3 ? (
              <Button type="button" onClick={nextStep} disabled={isPending}>
                Continue
              </Button>
            ) : (
              <Button type="submit" className="w-full" disabled={isPending}>
                {isPending ? "Submitting account..." : "Submit Application"}
              </Button>
            )}
          </div>

          <p className="text-center text-sm text-muted-foreground">
            Already have an account? {" "}
            <Link href="/auth/login" className="font-medium text-[#008753] hover:underline">
              Sign in
            </Link>
          </p>
        </form>
      </CardContent>
    </Card>
  )
}
