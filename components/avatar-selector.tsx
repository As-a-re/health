"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { User, UserCheck, Stethoscope } from "lucide-react"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"

interface AvatarSelectorProps {
  selectedAvatar: "male" | "female" | null
  onAvatarChange: (avatar: "male" | "female" | null) => void
  size?: 'sm' | 'md' | 'lg'
}

const sizeClasses = {
  sm: {
    button: 'h-8 w-8',
    icon: 'h-3 w-3',
    text: 'text-xs',
  },
  md: {
    button: 'h-10 w-10',
    icon: 'h-4 w-4',
    text: 'text-sm',
  },
  lg: {
    button: 'h-12 w-12',
    icon: 'h-5 w-5',
    text: 'text-base',
  },
}

const avatarOptions = [
  {
    id: "female" as const,
    name: "Dr. Ama Osei",
    title: "General Practitioner",
    description: "Warm, caring family doctor with 8 years experience",
    vrmModel: "/models/female-doctor.vrm",
    thumbnail: "/placeholder.svg?height=120&width=120",
    voice: "Warm female voice with gentle Ghanaian accent",
    personality: "Empathetic, patient, and thorough in explanations",
  },
  {
    id: "male" as const,
    name: "Dr. Kwame Asante",
    title: "Internal Medicine Specialist",
    description: "Experienced physician specializing in adult healthcare",
    vrmModel: "/models/male-doctor.vrm",
    thumbnail: "/placeholder.svg?height=120&width=120",
    voice: "Deep male voice with calm Ghanaian accent",
    personality: "Confident, reassuring, and detail-oriented",
  },
]

export function AvatarSelector({ selectedAvatar, onAvatarChange, size = 'md' }: AvatarSelectorProps) {
  const [isOpen, setIsOpen] = useState(false)
  const sizeClass = sizeClasses[size] || sizeClasses.md
  const selectedDoctor = avatarOptions.find((avatar) => avatar.id === selectedAvatar)

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button variant="outline" className={`flex items-center gap-2 bg-transparent ${sizeClass.button}`}>
          {selectedAvatar ? (
            <>
              <div className={`${sizeClass.button} rounded-full overflow-hidden border-2 border-blue-200`}>
                <img
                  src={selectedDoctor?.thumbnail}
                  alt={selectedDoctor?.name}
                  className="w-full h-full object-cover"
                />
              </div>
              <span className={`hidden sm:inline ${sizeClass.text}`}>{selectedDoctor?.name.split(' ')[1]}</span>
            </>
          ) : (
            <User className={sizeClass.icon} />
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-96 p-0" align="end">
        <div className="p-4 border-b bg-gradient-to-r from-blue-50 to-green-50">
          <h3 className="font-semibold flex items-center gap-2 text-lg">
            <Stethoscope className="h-5 w-5 text-blue-600" />
            Choose Your 3D AI Doctor
          </h3>
          <p className="text-sm text-gray-600 mt-1">Select a realistic 3D virtual doctor to assist you</p>
        </div>
        <div className="p-3 space-y-3">
          {avatarOptions.map((option) => (
            <div key={option.id} className="flex items-center gap-3 p-2 hover:bg-gray-50 rounded-lg cursor-pointer"
                 onClick={() => {
                   onAvatarChange(option.id)
                   setIsOpen(false)
                 }}>
              <div className={`${sizeClass.button} rounded-full overflow-hidden border-2 ${selectedAvatar === option.id ? 'border-blue-500' : 'border-gray-200'}`}>
                <img
                  src={option.thumbnail}
                  alt={option.name}
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="flex-1 min-w-0">
                <h4 className={`font-medium ${sizeClass.text}`}>{option.name}</h4>
                <p className={`text-gray-500 ${sizeClass.text}`}>{option.title}</p>
              </div>
              {selectedAvatar === option.id && (
                <UserCheck className={`${sizeClass.icon} text-blue-500`} />
              )}
            </div>
          ))}
          <Button
            variant="ghost"
            className="w-full justify-start text-gray-600 hover:bg-gray-100"
            onClick={() => {
              onAvatarChange(null)
              setIsOpen(false)
            }}
          >
            <User className={sizeClass.icon} />
            Continue without 3D Doctor (Text Only)
          </Button>
        </div>
      </PopoverContent>
    </Popover>
  )
}
