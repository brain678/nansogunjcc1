"use client"

import React, { useState, useRef, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Camera, CheckCircle, AlertCircle } from "lucide-react"

export function QrScanner() {
  const [manualCode, setManualCode] = useState("")
  const [scanResult, setScanResult] = useState<{
    success: boolean
    name: string
    memberId: string
    event: string
    checkedIn: boolean
  } | null>(null)

  // Mock QR scan result
  const handleQrScan = (qrCode: string) => {
    // In production, this would call an API to verify the QR code
    const mockResult = {
      success: true,
      name: "John Doe",
      memberId: qrCode.split("-")[0],
      event: "Monthly General Meeting",
      checkedIn: true,
    }
    setScanResult(mockResult)
  }

  const handleManualScan = () => {
    if (manualCode) {
      handleQrScan(manualCode)
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">QR Code Scanner</h1>
        <p className="text-muted-foreground mt-2">Scan member QR codes for check-in</p>
      </div>

      {/* Scanner Option */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Camera className="h-5 w-5" />
            Open Camera Scanner
          </CardTitle>
          <CardDescription>Use your device's camera to scan QR codes</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="bg-muted rounded-lg h-64 flex items-center justify-center mb-4">
            <div className="text-center">
              <Camera className="h-12 w-12 text-muted-foreground mx-auto mb-2" />
              <p className="text-muted-foreground">Camera scanner (requires device camera)</p>
            </div>
          </div>
          <Button className="w-full">
            <Camera className="mr-2 h-4 w-4" />
            Start Camera
          </Button>
        </CardContent>
      </Card>

      {/* Manual Entry */}
      <Card>
        <CardHeader>
          <CardTitle>Manual Code Entry</CardTitle>
          <CardDescription>Or enter the QR code manually</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Input
              placeholder="Paste or type QR code here..."
              value={manualCode}
              onChange={(e) => setManualCode(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleManualScan()}
            />
          </div>
          <Button onClick={handleManualScan} disabled={!manualCode}>
            Scan QR Code
          </Button>
        </CardContent>
      </Card>

      {/* Scan Result */}
      {scanResult && (
        <Card className={scanResult.success ? "border-green-500" : "border-red-500"}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {scanResult.success ? (
                <>
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  Check-in Successful
                </>
              ) : (
                <>
                  <AlertCircle className="h-5 w-5 text-red-500" />
                  Invalid QR Code
                </>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {scanResult.success && (
              <>
                <div className="border-b pb-3">
                  <p className="text-sm text-muted-foreground">Member</p>
                  <p className="text-lg font-bold">{scanResult.name}</p>
                  <p className="text-xs text-muted-foreground font-mono">{scanResult.memberId}</p>
                </div>

                <div className="border-b pb-3">
                  <p className="text-sm text-muted-foreground">Event</p>
                  <p className="font-medium">{scanResult.event}</p>
                </div>

                <div>
                  <Badge variant="success" className="text-base">
                    ✓ Checked In
                  </Badge>
                </div>

                <Button
                  variant="outline"
                  className="w-full"
                  onClick={() => {
                    setScanResult(null)
                    setManualCode("")
                  }}
                >
                  Scan Another
                </Button>
              </>
            )}
          </CardContent>
        </Card>
      )}

      {/* Recent Scans */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Scans</CardTitle>
          <CardDescription>Today's check-ins</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between items-center pb-2 border-b">
              <span>Sarah Johnson (MEM001)</span>
              <Badge variant="success">✓ 9:00 AM</Badge>
            </div>
            <div className="flex justify-between items-center pb-2 border-b">
              <span>Michael Chen (MEM002)</span>
              <Badge variant="success">✓ 9:05 AM</Badge>
            </div>
            <div className="flex justify-between items-center">
              <span>Emily Davis (MEM003)</span>
              <Badge variant="success">✓ 9:12 AM</Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
