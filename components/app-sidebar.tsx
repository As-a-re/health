"use client"

import { MessageCircle, FileText, User, Heart, LogOut } from "lucide-react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/hooks/use-auth"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarHeader,
} from "@/components/ui/sidebar"
import { Button } from "@/components/ui/button"

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
  const { logout } = useAuth()
  const router = useRouter()

  const handleSignOut = async () => {
    try {
      await logout()
      router.push('/login')
      router.refresh() // Ensure the page refreshes to update auth state
    } catch (error) {
      console.error('Sign out error:', error)
    }
  }

  return (
    <Sidebar>
      <SidebarHeader className="p-4">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-blue-100 rounded-lg">
            <Heart className="h-6 w-6 text-blue-600" />
          </div>
          <div>
            <h2 className="font-semibold">Health Assistant</h2>
            <p className="text-sm text-gray-600">Akan Support</p>
          </div>
        </div>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Navigation</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {menuItems.map((item) => (
                <SidebarMenuItem key={item.view}>
                  <SidebarMenuButton onClick={() => setActiveView(item.view)} isActive={activeView === item.view}>
                    <item.icon className="h-4 w-4" />
                    <span>{item.title}</span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter className="p-4">
        <Button 
          variant="outline" 
          className="w-full bg-transparent hover:bg-red-50 hover:text-red-600"
          onClick={handleSignOut}
        >
          <LogOut className="h-4 w-4 mr-2" />
          Sign Out
        </Button>
      </SidebarFooter>
    </Sidebar>
  )
}
