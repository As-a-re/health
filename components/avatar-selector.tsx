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

export function AvatarSelector({ selectedAvatar, onAvatarChange }: AvatarSelectorProps) {
  const [isOpen, setIsOpen] = useState(false)

  const selectedDoctor = avatarOptions.find((avatar) => avatar.id === selectedAvatar)

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button variant="outline" className="flex items-center gap-2 h-10 bg-transparent">
          {selectedAvatar ? (
            <>
              <div className="w-8 h-8 rounded-full overflow-hidden border-2 border-blue-200">
                <img
                  src={selectedDoctor?.thumbnail || "/placeholder.svg"}
                  alt={selectedDoctor?.name}
                  className="w-full h-full object-cover object-top"
                />
              </div>
              <span className="hidden sm:inline font-medium">{selectedDoctor?.name}</span>
            </>
          ) : (
            <>
              <User className="h-4 w-4" />
              <span className="hidden sm:inline">Choose Your Doctor</span>
            </>
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
          {avatarOptions.map((avatar) => (
            <Card
              key={avatar.id}
              className={`cursor-pointer transition-all hover:bg-gray-50 hover:shadow-md ${
                selectedAvatar === avatar.id ? "ring-2 ring-blue-500 bg-blue-50 shadow-lg" : ""
              }`}
              onClick={() => {
                onAvatarChange(avatar.id)
                setIsOpen(false)
              }}
            >
              <CardContent className="p-4">
                <div className="flex items-start gap-4">
                  <div className="relative">
                    <div className="w-20 h-24 rounded-lg overflow-hidden border-2 border-gray-200 bg-gradient-to-b from-blue-100 to-white">
                      <img
                        src={avatar.thumbnail || "/placeholder.svg"}
                        alt={avatar.name}
                        className="w-full h-full object-cover object-top"
                      />
                    </div>
                    {selectedAvatar === avatar.id && (
                      <div className="absolute -top-2 -right-2 w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center shadow-lg">
                        <UserCheck className="h-4 w-4 text-white" />
                      </div>
                    )}
                    <div className="absolute -bottom-1 left-1/2 transform -translate-x-1/2 bg-green-500 text-white px-2 py-0.5 rounded text-xs font-bold">
                      3D
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <h4 className="font-semibold text-base">{avatar.name}</h4>
                      <Badge variant="secondary" className="bg-blue-100 text-blue-800 text-xs">
                        {avatar.title}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-700 mb-2">{avatar.description}</p>
                    <div className="space-y-1">
                      <p className="text-xs text-blue-600 flex items-center gap-1">
                        <span>🎤</span> {avatar.voice}
                      </p>
                      <p className="text-xs text-green-600 flex items-center gap-1">
                        <span>👤</span> {avatar.personality}
                      </p>
                      <p className="text-xs text-purple-600 flex items-center gap-1">
                        <span>🎮</span> Interactive 3D Model
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}

          <Button
            variant="ghost"
            className="w-full justify-start text-gray-600 hover:bg-gray-100"
            onClick={() => {
              onAvatarChange(null)
              setIsOpen(false)
            }}
          >
            <User className="h-4 w-4 mr-2" />
            Continue without 3D Doctor (Text Only)
          </Button>
        </div>
      </PopoverContent>
    </Popover>
  )
}
