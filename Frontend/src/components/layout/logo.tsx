"use client"

import Image from "next/image"

export function Logo({ className }: { className?: string }) {
  return (
    <div className={className ?? "flex items-center gap-3"}>
      <div className="relative h-12 w-12 overflow-hidden rounded-full border border-[#008753]/20 bg-white shadow-sm">
        <Image src="/nans-logo.jpg" alt="NANS logo" fill sizes="48px" className="object-cover" />
      </div>
      <div className="flex flex-col leading-tight">
        <span className="text-lg font-black tracking-[0.08em] text-white drop-shadow-sm">NANS</span>
        <span className="text-xs font-semibold uppercase tracking-[0.24em] text-white drop-shadow-sm">Ogun JCC Axis</span>
      </div>
    </div>
  )
}
