"use client"

import { useState, useEffect } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Volume2, VolumeX, Heart, Maximize2 } from "lucide-react"
import { Simple3DDoctor } from "@/components/simple-3d-doctor"

interface AIDoctorAvatarProps {
  avatar: "male" | "female"
  isSpeaking: boolean
  isListening: boolean
  currentMessage?: string
  onSpeechToggle: () => void
  speechEnabled: boolean
  size?: 'sm' | 'md' | 'lg'
}

const doctorData = {
  female: {
    name: "Dr. Ama Osei",
    title: "General Practitioner",
    vrmModel: "/models/female-doctor.vrm",
    thumbnail: "/placeholder.svg?height=80&width=80",
  },
  male: {
    name: "Dr. Kwame Asante",
    title: "Internal Medicine Specialist",
    vrmModel: "/models/male-doctor.vrm",
    thumbnail: "/placeholder.svg?height=80&width=80",
  },
}

const sizeClasses = {
  sm: {
    container: 'w-12 h-12',
    text: 'text-xs',
    icon: 'h-3 w-3',
  },
  md: {
    container: 'w-16 h-16',
    text: 'text-sm',
    icon: 'h-4 w-4',
  },
  lg: {
    container: 'w-24 h-24',
    text: 'text-base',
    icon: 'h-5 w-5',
  },
}

export function AIDoctorAvatar({
  avatar,
  isSpeaking,
  isListening,
  currentMessage,
  onSpeechToggle,
  speechEnabled,
  size = 'md',
}: AIDoctorAvatarProps) {
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [emotion, setEmotion] = useState<"neutral" | "happy" | "concerned" | "focused">("neutral")

  const doctor = doctorData[avatar]

  const sizeClass = sizeClasses[size] || sizeClasses.md

  // Update emotion based on conversation state
  useEffect(() => {
    if (isSpeaking) {
      setEmotion("focused")
    } else if (isListening) {
      setEmotion("happy")
    } else {
      setEmotion("neutral")
    }
  }, [isSpeaking, isListening])

  const getStatusText = () => {
    if (isSpeaking) return "Speaking with you..."
    if (isListening) return "Listening carefully..."
    return "Ready for consultation"
  }

  const getStatusColor = () => {
    if (isSpeaking) return "text-green-600"
    if (isListening) return "text-blue-600"
    return "text-gray-600"
  }

  return (
    <Card className={`w-full max-w-sm mx-auto bg-gradient-to-b from-blue-50 to-white border-2 border-blue-100 shadow-lg ${sizeClass.container}`}>
      <CardContent className="p-4">
        {/* Doctor Info Header */}
        <div className="text-center mb-4">
          <h3 className={`font-bold text-lg text-gray-800 ${sizeClass.text}`}>{doctor.name}</h3>
          <Badge variant="secondary" className="bg-blue-100 text-blue-800">
            {doctor.title}
          </Badge>
          <Badge variant="outline" className="ml-2 bg-purple-100 text-purple-800">
            3D AI Doctor
          </Badge>
        </div>

        {/* 3D VRM Avatar Viewer */}
        <div className="relative mb-4">
          <div
            className={`relative overflow-hidden rounded-lg bg-white border-2 transition-all duration-300 ${
              isSpeaking
                ? "border-green-400 shadow-green-200 shadow-lg"
                : isListening
                  ? "border-blue-400 shadow-blue-200 shadow-lg"
                  : "border-gray-200"
            }`}
            style={{ height: "320px" }}
          >
            <Simple3DDoctor gender={avatar} isSpeaking={isSpeaking} isListening={isListening} emotion={emotion} />

            {/* Fullscreen Button */}
            <Button
              variant="ghost"
              size="sm"
              className="absolute top-2 right-2 bg-white/80 hover:bg-white"
              onClick={() => setIsFullscreen(!isFullscreen)}
            >
              <Maximize2 className={`h-4 w-4 ${sizeClass.icon}`} />
            </Button>

            {/* Vital Signs Animation (when active) */}
            {(isSpeaking || isListening) && (
              <div className="absolute top-2 left-2">
                <div className="bg-white/90 rounded-full p-2 shadow-lg">
                  <Heart className={`h-4 w-4 text-red-500 ${isSpeaking ? "animate-pulse" : ""}`} />
                </div>
              </div>
            )}
          </div>

          {/* Audio Visualization */}
          {isSpeaking && (
            <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2">
              <div className="flex items-center gap-1 bg-green-500 rounded-full px-3 py-1">
                {[...Array(5)].map((_, i) => (
                  <div
                    key={i}
                    className="w-1 bg-white rounded-full animate-pulse"
                    style={{
                      height: `${Math.random() * 12 + 6}px`,
                      animationDelay: `${i * 0.1}s`,
                    }}
                  />
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Status and Controls */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div
                className={`w-3 h-3 rounded-full ${
                  isSpeaking ? "bg-green-500 animate-pulse" : isListening ? "bg-blue-500 animate-pulse" : "bg-gray-400"
                }`}
              />
              <span className={`text-sm font-medium ${getStatusColor()}`}>{getStatusText()}</span>
            </div>

            <Button
              variant="outline"
              size="sm"
              onClick={onSpeechToggle}
              className={`${
                speechEnabled ? "text-green-600 border-green-200 hover:bg-green-50" : "text-gray-400 border-gray-200"
              }`}
            >
              {speechEnabled ? <Volume2 className={`h-4 w-4 ${sizeClass.icon}`} /> : <VolumeX className={`h-4 w-4 ${sizeClass.icon}`} />}
            </Button>
          </div>

          {/* 3D Model Info */}
          <div className="text-center text-xs text-gray-500 bg-gray-50 rounded-lg p-2">
            <p className="flex items-center justify-center gap-1">
              <span>🎮</span> Interactive 3D Model
            </p>
            <p>Drag to rotate • Realistic human movements</p>
          </div>

          {/* Current Message Preview */}
          {currentMessage && isSpeaking && (
            <div className="p-2 bg-green-50 rounded-lg border border-green-200">
              <p className="text-xs text-green-800 line-clamp-2">"{currentMessage.substring(0, 80)}..."</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
