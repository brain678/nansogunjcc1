"use client"

import React, { useRef } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useAuthStore } from "@/store/auth"
import { Download, Printer, Share2, QrCode } from "lucide-react"
import html2canvas from "html2canvas"
import jsPDF from "jspdf"

export function DigitalIdCard() {
  const user = useAuthStore((state) => state.user)
  const cardRef = useRef<HTMLDivElement>(null)

  if (!user) {
    return <div>Loading...</div>
  }

  // Generate a simple QR code (in production, use the API QR token)
  const qrCodeUrl = `https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${user.id}-NANS-MEM`

  const downloadCard = async () => {
    if (!cardRef.current) return

    try {
      const canvas = await html2canvas(cardRef.current, {
        backgroundColor: "#ffffff",
        scale: 2,
      })

      const pdf = new jsPDF({
        orientation: "landscape",
        unit: "mm",
        format: "a5",
      })

      const imgData = canvas.toDataURL("image/png")
      pdf.addImage(imgData, "PNG", 10, 10, 140, 90)
      pdf.save("nans-id-card.pdf")
    } catch (error) {
      console.error("Failed to download card:", error)
    }
  }

  const printCard = async () => {
    if (!cardRef.current) return

    try {
      const canvas = await html2canvas(cardRef.current, {
        backgroundColor: "#ffffff",
        scale: 2,
      })

      const printWindow = window.open("", "", "height=600,width=800")
      if (printWindow) {
        const img = canvas.toDataURL("image/png")
        printWindow.document.write(`
          <html>
            <head><title>Print ID Card</title></head>
            <body style="margin:0;padding:20px;text-align:center;">
              <img src="${img}" style="max-width:100%;height:auto;"/>
            </body>
          </html>
        `)
        printWindow.document.close()
        setTimeout(() => printWindow.print(), 250)
      }
    } catch (error) {
      console.error("Failed to print card:", error)
    }
  }

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">My Digital ID Card</h1>
          <p className="text-muted-foreground mt-2">Your NANS membership identification</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={printCard}>
            <Printer className="mr-2 h-4 w-4" />
            Print
          </Button>
          <Button variant="outline" size="sm" onClick={downloadCard}>
            <Download className="mr-2 h-4 w-4" />
            Download
          </Button>
          <Button variant="outline" size="sm">
            <Share2 className="mr-2 h-4 w-4" />
            Share
          </Button>
        </div>
      </div>

      {/* ID Card */}
      <div className="flex justify-center py-8 bg-muted rounded-lg">
        <div
          ref={cardRef}
          className="w-full max-w-md bg-gradient-to-br from-primary via-primary/90 to-primary/80 rounded-xl p-6 text-white shadow-2xl"
          style={{
            aspectRatio: "16/10",
            backgroundImage:
              "linear-gradient(135deg, rgba(59, 130, 246, 1) 0%, rgba(37, 99, 235, 1) 100%)",
          }}
        >
          <div className="h-full flex flex-col justify-between">
            {/* Top Section */}
            <div>
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h2 className="text-2xl font-bold">NANS</h2>
                  <p className="text-sm text-blue-100">Member Card</p>
                </div>
                <img src={qrCodeUrl} alt="QR Code" className="w-20 h-20 bg-white p-1 rounded" />
              </div>
            </div>

            {/* Member Info */}
            <div className="border-t border-white/20 pt-4">
              <div className="mb-3">
                <p className="text-xs text-blue-100 uppercase">Member Name</p>
                <p className="text-lg font-bold">
                  {user.firstName} {user.lastName}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4 text-xs">
                <div>
                  <p className="text-blue-100 uppercase">Member ID</p>
                  <p className="font-mono font-bold">{user.id.slice(0, 8).toUpperCase()}</p>
                </div>
                <div>
                  <p className="text-blue-100 uppercase">Status</p>
                  <p className="font-bold">Active</p>
                </div>
              </div>

              <div className="mt-3">
                <p className="text-xs text-blue-100 uppercase">Valid Until</p>
                <p className="text-sm font-bold">{new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toLocaleDateString()}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Card Info */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground mb-2">Member Status</p>
            <Badge variant="success" className="text-base">
              ✓ Active
            </Badge>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground mb-2">Card Valid Until</p>
            <p className="font-bold text-sm">
              {new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toLocaleDateString()}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground mb-2">Card Type</p>
            <p className="font-bold text-sm">Digital Membership Card</p>
          </CardContent>
        </Card>
      </div>

      {/* Instructions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <QrCode className="h-5 w-5" />
            How to Use Your ID Card
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex gap-3">
            <div className="flex-shrink-0 flex items-center justify-center h-8 w-8 rounded-full bg-primary text-white font-bold text-sm">
              1
            </div>
            <div>
              <p className="font-medium">Show QR Code at Events</p>
              <p className="text-sm text-muted-foreground">
                Display the QR code on your device at meetings and activities for quick check-in
              </p>
            </div>
          </div>

          <div className="flex gap-3">
            <div className="flex-shrink-0 flex items-center justify-center h-8 w-8 rounded-full bg-primary text-white font-bold text-sm">
              2
            </div>
            <div>
              <p className="font-medium">Print for Offline Use</p>
              <p className="text-sm text-muted-foreground">
                Download and print your card to carry in your wallet as a physical backup
              </p>
            </div>
          </div>

          <div className="flex gap-3">
            <div className="flex-shrink-0 flex items-center justify-center h-8 w-8 rounded-full bg-primary text-white font-bold text-sm">
              3
            </div>
            <div>
              <p className="font-medium">Verify Your Identity</p>
              <p className="text-sm text-muted-foreground">
                Your unique QR code ensures secure verification of your membership status
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Security Info */}
      <Card>
        <CardHeader>
          <CardTitle>Card Security</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <p>
            ✓ Your card is tied to your unique member ID and cannot be forged
          </p>
          <p>
            ✓ The QR code is encrypted and verified in real-time during check-in
          </p>
          <p>
            ✓ Lost or stolen cards can be deactivated immediately through your account
          </p>
          <p>
            ✓ Only valid for the membership period shown on your card
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
