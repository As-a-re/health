"use client"

import { MessageCircle, FileText, User, Heart, LogOut } from "lucide-react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/hooks/use-auth"
import { Sidebar, SidebarContent, SidebarFooter, SidebarGroup, SidebarGroupContent, SidebarGroupLabel, SidebarMenu, SidebarMenuButton, SidebarMenuItem, SidebarHeader } from "@/components/ui/sidebar"
import { Button } from "@/components/ui/button"
import { AvatarSelector } from "@/components/avatar-selector"
import { LanguageToggle } from "@/components/language-toggle"
import { Badge } from "@/components/ui/badge"
import { PlusCircle, Download, Trash2, Settings } from "lucide-react"

interface AppSidebarProps {
  activeView: "chat" | "records" | "profile"
  setActiveView: (view: "chat" | "records" | "profile") => void
}

const menuItems = [
  {
    title: "Chat Assistant",
    icon: MessageCircle,
    view: "chat" as const,
  },
  {
    title: "Health Records",
    icon: FileText,
    view: "records" as const,
  },
  {
    title: "Profile",
    icon: User,
    view: "profile" as const,
  },
]

export function AppSidebar({ activeView, setActiveView }: AppSidebarProps) {
  const { logout, user } = useAuth()
  const router = useRouter()

  const handleSignOut = async () => {
    try {
      await logout()
      router.push('/login')
      router.refresh()
    } catch (error) {
      console.error('Sign out error:', error)
    }
  }

  return (
    <Sidebar
      className="h-full bg-white border-r border-gray-200 transform-none"
      variant="sidebar"
      style={{
        transform: 'none',
        willChange: 'auto',
        backfaceVisibility: 'visible',
        WebkitBackfaceVisibility: 'visible',
        WebkitFontSmoothing: 'antialiased',
      }}
    >
      <SidebarHeader className="p-4 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-blue-600 shadow-sm">
            <Heart className="h-6 w-6 text-white" />
          </div>
          <div className="min-w-0">
            <h2 className="font-semibold text-gray-900">Health Assistant</h2>
            <p className="text-xs text-gray-500">Akan Support</p>
          </div>
        </div>
      </SidebarHeader>

      <SidebarContent className="p-4 space-y-4">
        {/* Profile card */}
        <div className="bg-white rounded-xl p-4 border border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-lg overflow-hidden bg-blue-100 flex items-center justify-center">
              <AvatarSelector selectedAvatar={null} onAvatarChange={() => {}} size="sm" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-gray-900 truncate">
                {user?.full_name || user?.email || 'Guest User'}
              </div>
              <div className="text-xs text-gray-500 truncate">
                {user?.email ? user.email : 'Not signed in'}
              </div>
            </div>
            <button className="p-1 rounded-md hover:bg-gray-100 text-gray-500">
              <Settings className="w-4 h-4" />
            </button>
          </div>

          <div className="mt-3 flex gap-2">
            <Button
              size="sm"
              className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
              onClick={() => {
                setActiveView('chat')
                if (typeof window !== 'undefined') {
                  window.dispatchEvent(new CustomEvent('new-chat'))
                }
              }}
            >
              <PlusCircle className="w-4 h-4 mr-2" /> 
              New Chat
            </Button>
            <Button size="sm" variant="outline" className="border-gray-300 text-gray-700">
              <Download className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Navigation */}
        <div className="space-y-1">
          <SidebarGroup>
            <SidebarGroupLabel className="text-xs font-medium text-gray-500 uppercase tracking-wider">
              Navigation
            </SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {menuItems.map((item) => (
                  <SidebarMenuItem key={item.view}>
                    <SidebarMenuButton 
                      onClick={() => setActiveView(item.view)} 
                      isActive={activeView === item.view}
                      className="text-gray-700 hover:bg-gray-100"
                    >
                      <item.icon className="h-4 w-4 text-gray-500" />
                      <span>{item.title}</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        </div>

        {/* Settings */}
        <div className="pt-4 border-t border-gray-200 space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">Language</span>
            <LanguageToggle 
              currentLanguage={"en"} 
              onLanguageChange={() => {}} 
              className="text-gray-500"
            />
          </div>

          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">Quick Actions</span>
            <div className="flex items-center gap-2">
              <Button 
                size="sm" 
                variant="ghost" 
                className="text-gray-500 hover:bg-gray-100"
                onClick={() => {}}
              >
                <Download className="w-4 h-4" />
              </Button>
              <Button 
                size="sm" 
                variant="ghost" 
                className="text-gray-500 hover:bg-gray-100"
                onClick={() => {}}
              >
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </SidebarContent>

      <SidebarFooter className="p-4 border-t border-gray-200">
        <Button 
          variant="outline" 
          className="w-full border-gray-300 text-gray-700 hover:bg-gray-50 hover:border-gray-400"
          onClick={handleSignOut}
        >
          <LogOut className="h-4 w-4 mr-2" />
          Sign Out
        </Button>
      </SidebarFooter>
    </Sidebar>
  )
}