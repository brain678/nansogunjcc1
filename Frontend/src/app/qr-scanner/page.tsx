import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { QrScanner } from "@/features/qr/qr-scanner"

export const metadata = {
  title: "QR Scanner - NANS Platform",
  description: "Scan member QR codes for check-in",
}

export default function QrScannerPage() {
  return (
    <DashboardLayout>
      <QrScanner />
    </DashboardLayout>
  )
}
