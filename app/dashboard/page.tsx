"use client"

import { useState } from "react"
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/app-sidebar"
import { ChatInterface } from "@/components/chat-interface"
import { HealthRecords } from "@/components/health-records"
import { UserProfile } from "@/components/user-profile"

export default function DashboardPage() {
  const [activeView, setActiveView] = useState<"chat" | "records" | "profile">("chat")
  const [selectedAvatar, setSelectedAvatar] = useState<"male" | "female" | null>("female")

  const renderContent = () => {
    switch (activeView) {
      case "chat":
        return <ChatInterface selectedAvatar={selectedAvatar} onAvatarChange={setSelectedAvatar} />
      case "records":
        return <HealthRecords />
      case "profile":
        return <UserProfile />
      default:
        return <ChatInterface selectedAvatar={selectedAvatar} onAvatarChange={setSelectedAvatar} />
    }
  }

  return (
    <SidebarProvider>
      <div className="min-h-screen w-full bg-slate-50">
        <div className="max-w-screen-2xl mx-auto w-full h-full flex">
          <AppSidebar activeView={activeView} setActiveView={setActiveView} />

          <main className="flex-1 flex flex-col mt-[0vh]">
            <header className="sticky top-0 z-20 border-b bg-white/80 backdrop-blur-sm p-4 flex items-center gap-4">
              <SidebarTrigger />
              <div>
                <h1 className="text-lg sm:text-xl font-semibold">Akan Health Assistant</h1>
                <p className="text-xs text-slate-500">Personalized health guidance in English and Akan</p>
              </div>
              {/* Doctor info aligned to the right of the header */}
              <div className="ml-auto hidden sm:flex flex-col items-end">
                <div className="text-sm font-semibold">{selectedAvatar === 'male' ? 'Dr. Kwame Asante' : 'Dr. Ama Osei'}</div>
                <div className="text-xs text-slate-500">General Practitioner</div>
              </div>
            </header>

            <div className="flex-1 p-4 overflow-auto">
              {renderContent()}
            </div>
          </main>
        </div>
      </div>
    </SidebarProvider>
  )
}
