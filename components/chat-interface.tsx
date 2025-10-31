"use client"

import type React from "react"
import { useState, useEffect, useRef, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Mic, Send, Volume2, Loader2, MicOff, Trash2, PlusCircle, Download, Settings } from "lucide-react"
import { AvatarSelector } from "@/components/avatar-selector"
import { LanguageToggle } from "@/components/language-toggle"
import { AIDoctorAvatar } from "@/components/ai-doctor-avatar"
import { api } from "@/lib/api"
import { useAuth } from "@/hooks/use-auth"
import { useSpeech } from "@/hooks/use-speech"

interface Message {
  id: string
  content: string
  sender: "user" | "assistant"
  timestamp: string
  language: "en" | "ak"
  confidence?: number
  model_used?: string
}

export function ChatInterface({
  selectedAvatar,
  onAvatarChange,
}: {
  selectedAvatar: "male" | "female" | null
  onAvatarChange: (a: "male" | "female" | null) => void
}) {
  const { user } = useAuth()
  const {
    isListening,
    transcript,
    startListening,
    stopListening,
    speak,
    error: speechError,
  } = useSpeech()

  const [isSpeaking, setIsSpeaking] = useState(false)
  const [speechOutputEnabled, setSpeechOutputEnabled] = useState(true)
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      content:
        "Hello! I'm your AI health assistant. I can help you with health questions in English and Akan. How are you feeling today?",
      sender: "assistant",
      timestamp: new Date().toISOString(),
      language: "en",
    },
  ])
  const [input, setInput] = useState("")
  const [isSending, setIsSending] = useState(false)
  const [language, setLanguage] = useState<"en" | "ak">("en")
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Update input message when speech recognition transcript changes
  useEffect(() => {
    if (transcript) {
      setInput(transcript)
    }
  }, [transcript])

  // Handle speech recognition errors
  useEffect(() => {
    if (speechError) console.error("Speech error:", speechError)
  }, [speechError])

  const sendMessage = useCallback(async () => {
    if (!input.trim() || isSending) return

    const messageText = input
    const userMessage: Message = {
      id: Date.now().toString(),
      content: messageText,
      sender: "user",
      timestamp: new Date().toISOString(),
      language: language,
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsSending(true)

    try {
      const response = await api.askHealthQuestion({
        question: messageText,
        language: language,
      })

      if (response.data) {
        const botMessage: Message = {
          id: Date.now().toString() + "-bot",
          content: response.data.response,
          sender: "assistant",
          timestamp: new Date().toISOString(),
          language: language,
        }
        setMessages((prev) => [...prev, botMessage])

        if (speechOutputEnabled) speak(response.data.response)
      }
    } catch (error) {
      console.error("Error sending message:", error)
      const errMessage: Message = {
        id: Date.now().toString() + "-err",
        content: "There was an error sending your message. Please try again.",
        sender: "assistant",
        timestamp: new Date().toISOString(),
        language: language,
      }
      setMessages((prev) => [...prev, errMessage])
    } finally {
      setIsSending(false)
    }
  }, [input, isSending, language, speak, speechOutputEnabled])

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const toggleSpeechInput = () => {
    if (isListening) stopListening()
    else {
      setInput("")
      startListening()
    }
  }

  const toggleSpeechOutput = () => {
    setSpeechOutputEnabled(!speechOutputEnabled)
    if (!speechOutputEnabled && messages.length > 0) {
      const lastMessage = [...messages].reverse().find((m) => m.sender === "assistant")
      if (lastMessage) speak(lastMessage.content)
    }
  }

  const clearConversation = () => setMessages([])

  useEffect(() => {
    const handler = () => setMessages([])
    window.addEventListener("new-chat", handler as EventListener)
    return () => window.removeEventListener("new-chat", handler as EventListener)
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const formatTime = (iso: string) => {
    try {
      const d = new Date(iso)
      return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    } catch {
      return ""
    }
  }

  const doctorProfile =
    selectedAvatar === "male"
      ? { name: "Dr Kwame Asante", title: "Internal Medicine Specialist" }
      : selectedAvatar === "female"
      ? { name: "Dr Ama Osei", title: "General Practitioner" }
      : { name: "AI Health Assistant", title: "" }

  return (
    <div className="w-full h-[calc(100vh-4rem)] p-3 sm:p-6 bg-transparent">
      <div className="h-full grid grid-cols-1 md:grid-cols-12 gap-6 items-start">

        {/* Left sidebar */}
        <aside className="md:col-span-4 lg:col-span-3 bg-white rounded-2xl shadow-sm p-4 flex flex-col gap-4">
          <div className="flex items-center gap-3">
            <AvatarSelector selectedAvatar={selectedAvatar} onAvatarChange={onAvatarChange} size="md" />
            <div>
              <div className="text-sm font-semibold truncate">{user?.email || "Guest User"}</div>
              <Badge variant={isListening ? "destructive" : "outline"} className="text-xs mt-1">
                {isListening ? "Listening" : "Ready"}
              </Badge>
            </div>
            <button className="ml-auto p-2 rounded-md hover:bg-slate-100" title="Settings">
              <Settings className="w-4 h-4 text-slate-600" />
            </button>
          </div>

          <div className="border-t border-slate-100 pt-3 overflow-y-auto flex-1">
            <div className="flex items-center justify-between mb-3">
              <div className="text-xs text-slate-600 font-medium">Conversations</div>
              <div className="flex items-center gap-2">
                <Button size="sm" variant="ghost" onClick={() => setMessages([])}>
                  <PlusCircle className="w-4 h-4 mr-1" /> New
                </Button>
                <Button size="sm" variant="ghost">
                  <Download className="w-4 h-4" />
                </Button>
              </div>
            </div>

            <ul className="space-y-2">
              {messages.slice(-5).reverse().map((m) => (
                <li key={m.id} className="flex items-center justify-between p-2 rounded-md hover:bg-slate-50">
                  <div className="min-w-0">
                    <div className="text-xs font-medium truncate">{m.sender === "user" ? "You" : "Assistant"}</div>
                    <div className="text-[11px] text-slate-500 truncate">{m.content.slice(0, 60)}</div>
                  </div>
                  <div className="text-[11px] text-slate-400 ml-2">{formatTime(m.timestamp)}</div>
                </li>
              ))}
            </ul>
          </div>

          <div className="pt-3 border-t border-slate-100 space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-600">
              <span>Language</span>
              <LanguageToggle currentLanguage={language} onLanguageChange={setLanguage} />
            </div>

            <div className="flex items-center justify-between text-xs text-slate-600">
              <span>Voice Output</span>
              <Button size="sm" variant={speechOutputEnabled ? "default" : "outline"} onClick={toggleSpeechOutput}>
                <Volume2 className="w-4 h-4 mr-1" />
                {speechOutputEnabled ? "On" : "Off"}
              </Button>
            </div>

            <div className="flex items-center justify-between text-xs text-slate-600">
              <span>Mic</span>
              <Button size="sm" variant={isListening ? "destructive" : "outline"} onClick={toggleSpeechInput}>
                {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
              </Button>
            </div>
          </div>

          <Button size="sm" variant="outline" onClick={clearConversation} className="w-full mt-3 flex items-center justify-center gap-2">
            <Trash2 className="w-4 h-4" /> Clear Conversation
          </Button>
        </aside>

        {/* Center column (avatar + chat) */}
        <main className="md:col-span-8 lg:col-span-9 bg-white rounded-2xl shadow-sm flex flex-col overflow-hidden">

          {/* 3D Avatar section on top */}
          <div className="flex-shrink-0 h-64 border-b bg-gradient-to-b from-slate-50 to-white flex items-center justify-center">
            <AIDoctorAvatar
              avatar={selectedAvatar || "female"}
              isSpeaking={isSpeaking}
              isListening={isListening}
              speechEnabled={speechOutputEnabled}
              onSpeechToggle={() => setSpeechOutputEnabled(!speechOutputEnabled)}
            />
          </div>

          {/* Chat header */}
          <div className="flex items-center justify-between p-4 border-b">
            <div className="flex items-center gap-3">
              <div>
                <div className="text-sm font-semibold">{doctorProfile.name}</div>
                <div className="text-xs text-slate-500">{doctorProfile.title}</div>
              </div>
            </div>
            <Badge variant={isListening ? "destructive" : "outline"} className="text-xs">
              {isListening ? "Listening" : "Idle"}
            </Badge>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gradient-to-b from-white to-slate-50">
            {messages.map((message) => (
              <div key={message.id} className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-[92%] sm:max-w-[78%] rounded-2xl p-3 shadow-sm ${
                    message.sender === "user"
                      ? "bg-gradient-to-r from-blue-600 to-teal-400 text-white"
                      : "bg-white border border-slate-100 text-slate-800"
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <div className="text-sm whitespace-pre-line">{message.content}</div>
                    <div className="text-[11px] text-slate-400 ml-2">{formatTime(message.timestamp)}</div>
                  </div>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Input area */}
          <div className="p-3 border-t bg-white">
            <div className="flex items-end gap-2">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={language === "en" ? "Type your message..." : "Twerɛ wo nkyerɛwee..."}
                className="flex-1 min-h-[44px] max-h-36 resize-none rounded-lg border border-slate-200 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-100"
              />

              <div className="flex flex-col items-center gap-2">
                <Button type="button" variant="ghost" size="icon" onClick={toggleSpeechInput}>
                  {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                </Button>

                <Button
                  type="button"
                  variant={speechOutputEnabled ? "default" : "outline"}
                  size="icon"
                  onClick={toggleSpeechOutput}
                >
                  <Volume2 className="w-4 h-4" />
                </Button>

                <Button
                  type="button"
                  onClick={sendMessage}
                  disabled={isSending || !input.trim()}
                  className="h-10 w-10 sm:w-auto sm:px-3"
                >
                  {isSending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                </Button>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
