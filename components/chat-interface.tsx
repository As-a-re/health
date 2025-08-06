"use client"

import type React from "react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Mic, Send, Volume2, Loader2 } from "lucide-react"
import { AvatarSelector } from "@/components/avatar-selector"
import { LanguageToggle } from "@/components/language-toggle"
import { AIDoctorAvatar } from "@/components/ai-doctor-avatar"
import { useState, useEffect, useRef } from "react"
import { api } from "@/lib/api"
import { useAuth } from "@/hooks/use-auth"

interface Message {
  id: string
  content: string
  sender: "user" | "assistant"
  timestamp: Date
  language: "en" | "ak"
  confidence?: number
  model_used?: string
}

export function ChatInterface() {
  const { user } = useAuth()
  const [selectedAvatar, setSelectedAvatar] = useState<"male" | "female" | null>("female")
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [speechEnabled, setSpeechEnabled] = useState(true)
  const [currentSpeakingMessage, setCurrentSpeakingMessage] = useState<string>("")
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      content:
        "Hello! I'm your AI health assistant. I can help you with health questions in English and Akan. How are you feeling today?",
      sender: "assistant",
      timestamp: new Date(),
      language: "en",
    },
  ])
  const [inputMessage, setInputMessage] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [currentLanguage, setCurrentLanguage] = useState<"en" | "ak">("en")
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    const lastMessage = messages[messages.length - 1]
    if (lastMessage?.sender === "assistant" && speechEnabled && selectedAvatar) {
      setTimeout(() => {
        setCurrentSpeakingMessage(lastMessage.content)
        speakResponse(lastMessage.content, lastMessage.language)
      }, 1000)
    }
  }, [messages, speechEnabled, selectedAvatar]) // Updated dependency array

  const speakResponse = (text: string, language: "en" | "ak") => {
    if (!speechEnabled || !selectedAvatar) return

    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel()

      const utterance = new SpeechSynthesisUtterance(text)
      utterance.lang = language === "en" ? "en-US" : "en-US"
      utterance.rate = 0.85
      utterance.pitch = selectedAvatar === "female" ? 1.2 : 0.8
      utterance.volume = 0.9

      utterance.onstart = () => {
        setIsSpeaking(true)
        setCurrentSpeakingMessage(text)
      }
      utterance.onend = () => {
        setIsSpeaking(false)
        setCurrentSpeakingMessage("")
      }
      utterance.onerror = () => {
        setIsSpeaking(false)
        setCurrentSpeakingMessage("")
      }

      window.speechSynthesis.speak(utterance)
    }
  }

  const toggleSpeech = () => {
    if (isSpeaking) {
      window.speechSynthesis.cancel()
      setIsSpeaking(false)
      setCurrentSpeakingMessage("")
    }
    setSpeechEnabled(!speechEnabled)
  }

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      sender: "user",
      timestamp: new Date(),
      language: currentLanguage,
    }

    setMessages((prev) => [...prev, userMessage])
    setInputMessage("")
    setIsLoading(true)

    try {
      const response = await api.askHealthQuestion({
        question: inputMessage,
        language: currentLanguage === "ak" ? "ak" : "en",
        include_translation: true,
      })

      if (response.data) {
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: response.data.response,
          sender: "assistant",
          timestamp: new Date(),
          language: response.data.language as "en" | "ak",
          confidence: response.data.confidence,
          model_used: response.data.model_used,
        }

        setMessages((prev) => [...prev, assistantMessage])
      } else {
        // Error message
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          content:
            "I apologize, but I'm having trouble processing your question right now. Please try again or consult with a healthcare professional.",
          sender: "assistant",
          timestamp: new Date(),
          language: "en",
        }
        setMessages((prev) => [...prev, errorMessage])
      }
    } catch (error) {
      console.error("Failed to send message:", error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "I'm sorry, there was an error processing your request. Please try again.",
        sender: "assistant",
        timestamp: new Date(),
        language: "en",
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const simulateListening = () => {
    setIsListening(true)
    setTimeout(() => setIsListening(false), 3000)
  }

  return (
    <div className="flex flex-col lg:flex-row h-full max-w-7xl mx-auto gap-6">
      {/* 3D AI Doctor Avatar Panel */}
      {selectedAvatar && (
        <div className="lg:w-80 flex-shrink-0">
          <AIDoctorAvatar
            avatar={selectedAvatar}
            isSpeaking={isSpeaking}
            isListening={isListening}
            currentMessage={currentSpeakingMessage}
            onSpeechToggle={toggleSpeech}
            speechEnabled={speechEnabled}
          />
        </div>
      )}

      {/* Chat Interface */}
      <div className="flex-1 flex flex-col">
        <div className="flex justify-between items-center mb-4">
          <div className="flex items-center gap-4">
            <h2 className="text-2xl font-bold">AI Health Consultation</h2>
            {selectedAvatar && (
              <Badge variant="secondary" className="bg-green-100 text-green-800">
                3D Live Session
              </Badge>
            )}
            {user && (
              <Badge variant="outline" className="bg-blue-50 text-blue-700">
                Logged in as {user.full_name || user.email}
              </Badge>
            )}
          </div>
          <div className="flex items-center gap-4">
            <AvatarSelector selectedAvatar={selectedAvatar} onAvatarChange={setSelectedAvatar} />
            <LanguageToggle currentLanguage={currentLanguage} onLanguageChange={setCurrentLanguage} />
          </div>
        </div>

        <Card className="flex-1 flex flex-col">
          <CardContent className="flex-1 p-4 overflow-y-auto space-y-4 max-h-[600px]">
            {!selectedAvatar && (
              <div className="text-center py-12 text-gray-500">
                <p className="text-lg mb-2">Choose a 3D AI Doctor to begin your consultation</p>
                <p className="text-sm">Select a realistic 3D doctor above to start your healthcare session</p>
              </div>
            )}

            {selectedAvatar &&
              messages.map((message) => (
                <div key={message.id} className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}>
                  {message.sender === "assistant" && (
                    <div className="flex items-start gap-3 max-w-[85%]">
                      <div className="w-10 h-10 rounded-full overflow-hidden border-2 border-blue-200 flex-shrink-0 bg-gradient-to-b from-blue-100 to-white">
                        <img
                          src={
                            selectedAvatar === "female"
                              ? "/placeholder.svg?height=40&width=40&query=3d+female+african+doctor+avatar+professional+headshot"
                              : "/placeholder.svg?height=40&width=40&query=3d+male+african+doctor+avatar+professional+headshot"
                          }
                          alt={`Dr. ${selectedAvatar === "female" ? "Ama" : "Kwame"}`}
                          className="w-full h-full object-cover"
                        />
                      </div>
                      <div className="bg-gray-100 text-gray-900 p-4 rounded-lg rounded-tl-none shadow-sm">
                        <p className="text-sm leading-relaxed">{message.content}</p>
                        <div className="flex items-center justify-between mt-3">
                          <span className="text-xs text-gray-500">
                            {new Date(message.timestamp).toLocaleTimeString('en-US', {
                              hour: '2-digit',
                              minute: '2-digit',
                              hour12: true
                            })}
                          </span>
                          <div className="flex items-center gap-2">
                            <Badge variant="outline" className="text-xs">
                              {message.language === "en" ? "EN" : "AK"}
                            </Badge>
                            {message.confidence && (
                              <Badge variant="outline" className="text-xs bg-green-50 text-green-600">
                                {Math.round(message.confidence * 100)}%
                              </Badge>
                            )}
                            {message.model_used && (
                              <Badge variant="outline" className="text-xs bg-purple-50 text-purple-600">
                                {message.model_used}
                              </Badge>
                            )}
                            {speechEnabled && (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => speakResponse(message.content, message.language)}
                                className="h-6 w-6 p-0 hover:bg-blue-100"
                              >
                                <Volume2 className="h-3 w-3 text-blue-600" />
                              </Button>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                  {message.sender === "user" && (
                    <div className="max-w-[80%] bg-blue-600 text-white p-4 rounded-lg rounded-tr-none shadow-sm">
                      <p className="text-sm leading-relaxed">{message.content}</p>
                      <div className="flex items-center justify-between mt-3">
                        <span className="text-xs text-blue-100">
                          {new Date(message.timestamp).toLocaleTimeString('en-US', {
                            hour: '2-digit',
                            minute: '2-digit',
                            hour12: true
                          })}
                        </span>
                        <Badge variant="outline" className="text-xs border-blue-300 text-blue-100">
                          {message.language === "en" ? "EN" : "AK"}
                        </Badge>
                      </div>
                    </div>
                  )}
                </div>
              ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="flex items-start gap-3 max-w-[85%]">
                  <div className="w-10 h-10 rounded-full overflow-hidden border-2 border-blue-200 flex-shrink-0 bg-gradient-to-b from-blue-100 to-white">
                    <img
                      src={
                        selectedAvatar === "female"
                          ? "/placeholder.svg?height=40&width=40&query=3d+female+african+doctor+avatar+professional+headshot"
                          : "/placeholder.svg?height=40&width=40&query=3d+male+african+doctor+avatar+professional+headshot"
                      }
                      alt={`Dr. ${selectedAvatar === "female" ? "Ama" : "Kwame"}`}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="bg-gray-100 text-gray-900 p-4 rounded-lg rounded-tl-none shadow-sm">
                    <div className="flex items-center gap-2">
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span className="text-sm">Analyzing your question...</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </CardContent>

          <div className="border-t p-4">
            <div className="flex gap-2">
              <Input
                placeholder={`Ask your health question in ${currentLanguage === "en" ? "English" : "Akan"}...`}
                className="flex-1"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                onFocus={() => selectedAvatar && simulateListening()}
                disabled={isLoading}
              />
              <Button
                variant="outline"
                size="icon"
                onClick={() => selectedAvatar && simulateListening()}
                className={isListening ? "bg-blue-100 text-blue-600" : ""}
                disabled={isLoading}
              >
                <Mic className="h-4 w-4" />
              </Button>
              <Button onClick={handleSendMessage} disabled={isLoading || !inputMessage.trim()}>
                {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
              </Button>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              {selectedAvatar
                ? `Your 3D AI doctor is ready to help with health questions in ${currentLanguage === "en" ? "English" : "Akan"}`
                : "Select a 3D AI doctor to begin your consultation"}
            </p>
          </div>
        </Card>
      </div>
    </div>
  )
}
