import { apiClient } from "@/lib/api-client"
import { API_ENDPOINTS } from "@/lib/config"
import { Meeting, Activity, Document, PaginatedResponse } from "@/types"

const normalizeDocument = (document: any): Document => ({
  id: document.id,
  title: document.title,
  description: document.description,
  fileUrl: document.fileUrl ?? document.file_url,
  fileSize: document.fileSize ?? document.file_size,
  fileType: document.fileType ?? document.file_type,
  category: document.category,
  uploadedBy: document.uploadedBy ?? document.uploaded_by,
  uploadedAt: document.uploadedAt ?? document.uploaded_at,
  version: document.version ?? 1,
})

const normalizeDocumentList = (payload: any): PaginatedResponse<Document> => {
  if (!payload || !Array.isArray(payload.items)) {
    return { total: 0, skip: 0, limit: 0, items: [] }
  }

  return {
    total: typeof payload.total === "number" ? payload.total : 0,
    skip: typeof payload.skip === "number" ? payload.skip : 0,
    limit: typeof payload.limit === "number" ? payload.limit : 0,
    items: payload.items.map(normalizeDocument),
  }
}

export const meetingService = {
  async list(
    skip: number = 0,
    limit: number = 10
  ): Promise<PaginatedResponse<Meeting>> {
    const params = new URLSearchParams()
    params.append("skip", skip.toString())
    params.append("limit", limit.toString())

    return apiClient.get<PaginatedResponse<Meeting>>(
      `${API_ENDPOINTS.meetings.list}?${params.toString()}`
    )
  },

  async getById(meetingId: string): Promise<Meeting> {
    return apiClient.get<Meeting>(
      API_ENDPOINTS.meetings.get.replace(":id", meetingId)
    )
  },

  async create(data: Partial<Meeting>): Promise<Meeting> {
    return apiClient.post<Meeting>(API_ENDPOINTS.meetings.create, data)
  },

  async update(meetingId: string, data: Partial<Meeting>): Promise<Meeting> {
    return apiClient.put<Meeting>(
      API_ENDPOINTS.meetings.update.replace(":id", meetingId),
      data
    )
  },

  async delete(meetingId: string): Promise<void> {
    return apiClient.delete(
      API_ENDPOINTS.meetings.delete.replace(":id", meetingId)
    )
  },
}

export const activityService = {
  async list(
    skip: number = 0,
    limit: number = 10
  ): Promise<PaginatedResponse<Activity>> {
    const params = new URLSearchParams()
    params.append("skip", skip.toString())
    params.append("limit", limit.toString())

    return apiClient.get<PaginatedResponse<Activity>>(
      `${API_ENDPOINTS.activities.list}?${params.toString()}`
    )
  },

  async getById(activityId: string): Promise<Activity> {
    return apiClient.get<Activity>(
      API_ENDPOINTS.activities.get.replace(":id", activityId)
    )
  },

  async create(data: Partial<Activity>): Promise<Activity> {
    return apiClient.post<Activity>(API_ENDPOINTS.activities.create, data)
  },

  async update(activityId: string, data: Partial<Activity>): Promise<Activity> {
    return apiClient.put<Activity>(
      API_ENDPOINTS.activities.update.replace(":id", activityId),
      data
    )
  },

  async delete(activityId: string): Promise<void> {
    return apiClient.delete(
      API_ENDPOINTS.activities.delete.replace(":id", activityId)
    )
  },
}

export const documentService = {
  async list(
    skip: number = 0,
    limit: number = 10,
    category?: string
  ): Promise<PaginatedResponse<Document>> {
    const params = new URLSearchParams()
    params.append("skip", skip.toString())
    params.append("limit", limit.toString())
    if (category) params.append("category", category)

    const payload = await apiClient.get<any>(
      `${API_ENDPOINTS.documents.list}?${params.toString()}`
    )
    return normalizeDocumentList(payload)
  },

  async getById(documentId: string): Promise<Document> {
    const payload = await apiClient.get<any>(
      API_ENDPOINTS.documents.get.replace(":id", documentId)
    )
    return normalizeDocument(payload)
  },

  async upload(file: File, category: string): Promise<Document> {
    const formData = new FormData()
    formData.append("file", file)
    formData.append("category", category)

    // Let axios set the multipart Content-Type and boundary
    const payload = await apiClient.post<any>(API_ENDPOINTS.documents.upload, formData)
    return normalizeDocument(payload)
  },

  async delete(documentId: string): Promise<void> {
    return apiClient.delete(
      API_ENDPOINTS.documents.delete.replace(":id", documentId)
    )
  },
}
