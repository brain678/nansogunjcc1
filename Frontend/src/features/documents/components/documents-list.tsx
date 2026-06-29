"use client"

import React from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { FileText, Download, Share2, Plus } from "lucide-react"
import Link from "next/link"

const mockDocuments = [
  {
    id: "1",
    title: "Constitution and Bylaws",
    category: "Legal",
    uploadedDate: new Date(2024, 0, 15),
    size: "2.4 MB",
    downloadCount: 45,
  },
  {
    id: "2",
    title: "Annual Report 2023",
    category: "Reports",
    uploadedDate: new Date(2024, 0, 10),
    size: "5.1 MB",
    downloadCount: 32,
  },
  {
    id: "3",
    title: "Meeting Minutes - December 2024",
    category: "Minutes",
    uploadedDate: new Date(2024, 1, 5),
    size: "1.8 MB",
    downloadCount: 18,
  },
]

export function DocumentsList() {
  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Documents</h1>
          <p className="text-muted-foreground mt-2">Access and share organization documents</p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Upload Document
        </Button>
      </div>

      {/* Documents List */}
      <div className="space-y-4">
        {mockDocuments.map((doc) => (
          <Card key={doc.id}>
            <CardContent className="pt-6">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-primary/10 rounded-lg">
                  <FileText className="h-6 w-6 text-primary" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold">{doc.title}</h3>
                  <div className="flex items-center gap-3 mt-2 text-sm text-muted-foreground">
                    <Badge variant="outline">{doc.category}</Badge>
                    <span>{doc.uploadedDate.toLocaleDateString()}</span>
                    <span>•</span>
                    <span>{doc.size}</span>
                    <span>•</span>
                    <span>{doc.downloadCount} downloads</span>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="icon" title="Download">
                    <Download className="h-4 w-4" />
                  </Button>
                  <Button variant="outline" size="icon" title="Share">
                    <Share2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
