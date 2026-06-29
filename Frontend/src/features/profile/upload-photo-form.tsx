"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { UseMutationResult } from "@tanstack/react-query"

interface UploadPhotoFormProps {
  mutation: UseMutationResult<any, Error, File, unknown>
  onSuccess?: () => void
}

const allowedTypes = ["image/jpeg", "image/png", "image/webp"]
const maxSizeInBytes = 5 * 1024 * 1024 // 5 MB

export function UploadPhotoForm({ mutation, onSuccess }: UploadPhotoFormProps) {
  const [file, setFile] = useState<File | null>(null)
  const [error, setError] = useState<string | null>(null)

  const validateFile = (file: File) => {
    if (!allowedTypes.includes(file.type)) {
      return "Only JPG, PNG, and WEBP images are allowed."
    }
    if (file.size > maxSizeInBytes) {
      return "File must be smaller than 5 MB."
    }
    return null
  }

  const onFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setError(null)
    const selectedFile = event.target.files?.[0]
    if (!selectedFile) {
      setFile(null)
      return
    }

    const validationError = validateFile(selectedFile)
    if (validationError) {
      setError(validationError)
      setFile(null)
      return
    }

    setFile(selectedFile)
  }

  const onSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!file) {
      setError("Please select a photo to upload.")
      return
    }

    await mutation.mutateAsync(file)
    onSuccess?.()
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <div>
        <Label htmlFor="photo">Profile Photo</Label>
        <input
          id="photo"
          type="file"
          accept={allowedTypes.join(",")}
          onChange={onFileChange}
          disabled={mutation.isPending}
          className="mt-2"
        />
        {error && <p className="text-xs text-destructive">{error}</p>}
      </div>
      <Button type="submit" disabled={!file || mutation.isPending}>
        Upload Photo
      </Button>
    </form>
  )
}
