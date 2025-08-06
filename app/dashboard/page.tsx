"use client"

import { useState } from "react"
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/app-sidebar"
import { ChatInterface } from "@/components/chat-interface"
import { HealthRecords } from "@/components/health-records"
import { UserProfile } from "@/components/user-profile"

export default function DashboardPage() {
  const [activeView, setActiveView] = useState<"chat" | "records" | "profile">("chat")

  const renderContent = () => {
    switch (activeView) {
      case "chat":
        return <ChatInterface />
      case "records":
        return <HealthRecords />
      case "profile":
        return <UserProfile />
      default:
        return <ChatInterface />
    }
  }

  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full">
        <AppSidebar activeView={activeView} setActiveView={setActiveView} />
        <main className="flex-1 flex flex-col">
          <header className="border-b bg-white p-4 flex items-center gap-4">
            <SidebarTrigger />
            <h1 className="text-xl font-semibold">Akan Health Assistant</h1>
          </header>
          <div className="flex-1 p-4">{renderContent()}</div>
        </main>
      </div>
    </SidebarProvider>
  )
}
