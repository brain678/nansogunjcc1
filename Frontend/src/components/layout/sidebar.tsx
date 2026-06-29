"use client"

import React, { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { Menu, X, LogOut, Settings } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useAuthStore } from "@/store/auth"
import { useLogout } from "@/hooks/use-auth"
import { userUtils } from "@/lib/utils"
import { cn } from "@/lib/cn"
import { Logo } from "@/components/layout/logo"

const navItems = {
  common: [
    { label: "Dashboard", href: "/dashboard", icon: "🏠" },
    { label: "My Profile", href: "/profile", icon: "👤" },
    { label: "My ID Card", href: "/my-id-card", icon: "🎫" },
  ],
  member: [
    { label: "Meetings", href: "/meetings", icon: "📅" },
    { label: "Activities", href: "/activities", icon: "🎯" },
    { label: "Documents", href: "/documents", icon: "📄" },
  ],
  chairman: [
    { label: "Members", href: "/members", icon: "👥" },
    { label: "Approvals", href: "/members/approve", icon: "✅" },
    { label: "Meetings", href: "/meetings", icon: "📅" },
    { label: "Activities", href: "/activities", icon: "🎯" },
  ],
  generalSecretary: [
    { label: "Members", href: "/members", icon: "👥" },
    { label: "Approvals", href: "/members/approve", icon: "✅" },
    { label: "Meetings", href: "/meetings", icon: "📅" },
    { label: "Activities", href: "/activities", icon: "🎯" },
    { label: "Documents", href: "/documents", icon: "📄" },
  ],
  admin: [
    { label: "Members", href: "/members", icon: "👥" },
    { label: "Approvals", href: "/members/approve", icon: "✅" },
    { label: "Meetings", href: "/meetings", icon: "📅" },
    { label: "Activities", href: "/activities", icon: "🎯" },
    { label: "Documents", href: "/documents", icon: "📄" },
    { label: "Admin Users", href: "/admin/users", icon: "🔐" },
    { label: "Audit Logs", href: "/admin/audit", icon: "📊" },
  ],
}

export function Sidebar() {
  const [isOpen, setIsOpen] = useState(false)
  const pathname = usePathname()
  const user = useAuthStore((state) => state.user)
  const { mutate: logout } = useLogout()

  const getUserNavItems = () => {
    if (!user) return navItems.common

    if (userUtils.isAdmin()) return [...navItems.common, ...navItems.admin]
    if (userUtils.isGeneralSecretary()) return [...navItems.common, ...navItems.generalSecretary]
    if (userUtils.isChairman()) return [...navItems.common, ...navItems.chairman]
    return [...navItems.common, ...navItems.member]
  }

  const items = getUserNavItems()

  const isActive = (href: string) => pathname === href || pathname.startsWith(href + "/")

  return (
    <>
      {/* Mobile menu button */}
      <Button
        variant="ghost"
        size="icon"
        className="fixed left-4 top-4 z-50 rounded-full border border-[#008753]/20 bg-white p-1 shadow-sm md:hidden"
        onClick={() => setIsOpen(!isOpen)}
        aria-label={isOpen ? "Close menu" : "Open menu"}
      >
        {isOpen ? <X /> : <Menu />}
      </Button>

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed left-0 top-0 z-40 h-screen w-64 overflow-y-auto border-r border-[#006f45]/20 bg-[#008753] text-white transition-transform duration-300",
          isOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        )}
      >
        <div className="p-6">
          <Logo />
        </div>

        <nav className="space-y-2 px-4 py-4">
          {items.map((item) => (
            <Link key={item.href} href={item.href}>
              <Button
                variant={isActive(item.href) ? "default" : "ghost"}
                className={cn(
                  "w-full justify-start",
                  isActive(item.href) ? "bg-[#006f45] text-white shadow-sm" : "text-white/90 hover:bg-[#006f45]/20 hover:text-white"
                )}
                onClick={() => setIsOpen(false)}
              >
                <span className="mr-3">{item.icon}</span>
                {item.label}
              </Button>
            </Link>
          ))}
        </nav>

        <div className="absolute bottom-4 left-4 right-4 space-y-2 border-t border-white/15 pt-4">
          <Link href="/settings">
            <Button variant="ghost" className="w-full justify-start text-white/90 hover:bg-[#006f45]/20 hover:text-white" size="sm">
              <Settings className="mr-2 h-4 w-4" />
              Settings
            </Button>
          </Link>
          <Button
            variant="destructive"
            className="w-full justify-start"
            size="sm"
            onClick={() => logout()}
          >
            <LogOut className="mr-2 h-4 w-4" />
            Logout
          </Button>
        </div>
      </aside>

      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 md:hidden z-30"
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  )
}
