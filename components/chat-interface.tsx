"use client"

import type React from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Mic, Send, Volume2, Loader2, MicOff, Trash2 } from "lucide-react"
import { AvatarSelector } from "@/components/avatar-selector"
import { LanguageToggle } from "@/components/language-toggle"
import { AIDoctorAvatar } from "@/components/ai-doctor-avatar"
import { useState, useEffect, useRef, useCallback } from "react"
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

export function ChatInterface() {
  const { user } = useAuth()
  const {
    isListening,
    transcript,
    startListening,
    stopListening,
    speak,
    error: speechError,
  } = useSpeech()
  
  const [selectedAvatar, setSelectedAvatar] = useState<"male" | "female" | null>("female")
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
    if (speechError) {
      console.error('Speech error:', speechError)
      // Optionally show error to user
    }
  }, [speechError])

  const sendMessage = useCallback(async () => {
    if (!input.trim() || isSending) return;

    const messageText = input
    const userMessage: Message = {
      id: Date.now().toString(),
      content: messageText,
      sender: 'user',
      timestamp: new Date().toISOString(),
      language: language,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsSending(true);

    try {
      const response = await api.askHealthQuestion({
        question: messageText,
        language: language,
      });

      if (response.data) {
        const botMessage: Message = {
          id: Date.now().toString() + '-bot',
          content: response.data.response,
          sender: 'assistant',
          timestamp: new Date().toISOString(),
          language: language,
        };
        setMessages((prev) => [...prev, botMessage]);

        // Speak the response if speech output is enabled
        if (speechOutputEnabled) {
          speak(response.data.response);
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errMessage: Message = {
        id: Date.now().toString() + '-err',
        content: 'There was an error sending your message. Please try again.',
        sender: 'assistant',
        timestamp: new Date().toISOString(),
        language: language,
      }
      setMessages((prev) => [...prev, errMessage])
    } finally {
      setIsSending(false);
    }
  }, [input, isSending, language, speak, speechOutputEnabled]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const toggleSpeechInput = () => {
    if (isListening) {
      stopListening()
    } else {
      setInput("")
      startListening()
    }
  }

  const toggleSpeechOutput = () => {
    setSpeechOutputEnabled(!speechOutputEnabled)
    if (!speechOutputEnabled && messages.length > 0) {
      // Speak the last assistant message when enabling speech
      const lastMessage = [...messages].reverse().find(m => m.sender === 'assistant')
      if (lastMessage) {
        speak(lastMessage.content)
      }
    }
  }

  const clearConversation = () => {
    setMessages([])
  }

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const formatTime = (iso: string) => {
    try {
      const d = new Date(iso)
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    } catch { return '' }
  }

  return (
    <div className="w-full h-[calc(100vh-4rem)] p-3 sm:p-6 bg-gray-50">
      <div className="h-full grid grid-cols-1 md:grid-cols-12 gap-4">
        {/* Left column: avatar selector + quick controls */}
        <aside className="md:col-span-3 bg-white rounded-2xl shadow-sm p-4 flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold">Profile</h3>
              <div className="text-xs text-slate-500">{user?.email || 'Guest'}</div>
            </div>
            <div className="hidden md:block">
              <AvatarSelector
                selectedAvatar={selectedAvatar}
                onAvatarChange={(avatar: "male" | "female" | null) => setSelectedAvatar(avatar)}
                size="md"
              />
            </div>
          </div>

          <div className="md:hidden">
            {/* Mobile avatar selector */}
            <AvatarSelector
              selectedAvatar={selectedAvatar}
              onAvatarChange={(avatar: "male" | "female" | null) => setSelectedAvatar(avatar)}
              size="sm"
            />
          </div>

          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-600">Language</span>
              <LanguageToggle currentLanguage={language} onLanguageChange={(lang: "en" | "ak") => setLanguage(lang)} />
            </div>

            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-600">Voice Output</span>
              <Button size="sm" variant={speechOutputEnabled ? "default" : "outline"} onClick={toggleSpeechOutput}>
                <div className="flex items-center gap-2"><Volume2 className="w-4 h-4"/>{speechOutputEnabled ? 'On' : 'Off'}</div>
              </Button>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-600">Mic</span>
              <Button size="sm" variant={isListening ? "destructive" : "outline"} onClick={toggleSpeechInput}>
                {isListening ? <MicOff className="w-4 h-4"/> : <Mic className="w-4 h-4"/>}
              </Button>
            </div>

            <div className="pt-2 border-t border-slate-100" />

            <div className="flex items-center gap-2">
              <Button size="sm" variant="ghost" onClick={() => { /* placeholder for export */ }}>Export</Button>
              <Button size="sm" variant="ghost" onClick={clearConversation}><Trash2 className="w-4 h-4"/></Button>
            </div>
          </div>

          <div className="mt-auto text-xs text-slate-400">
            Tips: Ask clearly and include symptoms or images for better guidance.
          </div>
        </aside>

        {/* Center column: messages + input */}
        <main className="md:col-span-6 bg-white rounded-2xl shadow-sm flex flex-col overflow-hidden">
          {/* Header (small) */}
          <div className="flex items-center justify-between p-4 border-b">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-blue-50 flex items-center justify-center">
                <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C8 2 5 5 5 9c0 1.2.3 2.3.9 3.3C6.3 15.2 9 18 12 22c3-4 5.7-6.8 6.1-9.7.6-1 .9-2.1.9-3.3 0-4-3-7-7-7z"/></svg>
              </div>
              <div>
                <div className="text-sm font-semibold">AI Health Assistant</div>
                <div className="text-xs text-slate-500">{isListening ? 'Listening...' : 'Ready'}</div>
              </div>
            </div>
            <div className="hidden sm:flex items-center gap-2">
              <Badge variant={isListening ? 'destructive' : 'outline'} className="text-xs">{isListening ? 'Listening' : 'Idle'}</Badge>
            </div>
          </div>

          {/* Messages area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gradient-to-b from-white to-slate-50">
            {messages.map((message) => (
              <div key={message.id} className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[92%] sm:max-w-[78%] rounded-2xl p-3 shadow-sm ${message.sender === 'user' ? 'bg-gradient-to-r from-blue-600 to-teal-400 text-white' : 'bg-white border border-slate-100 text-slate-800'}`}>
                  <div className="flex items-center justify-between gap-2">
                    <div className="text-sm whitespace-pre-line">{message.content}</div>
                    <div className="text-[11px] text-slate-400 ml-2">{formatTime(message.timestamp)}</div>
                  </div>
                  {message.sender === 'assistant' && message.model_used && (
                    <div className="mt-2 text-xs text-slate-500">Model: {message.model_used} {message.confidence && `• ${(message.confidence*100).toFixed(1)}%`}</div>
                  )}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Input area (stays at bottom of center column) */}
          <div className="p-3 border-t bg-white">
            <div className="flex items-end gap-2">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={language === 'en' ? 'Type your message...' : 'Twerɛ wo nkyerɛwee...'}
                className="flex-1 min-h-[44px] max-h-36 resize-none rounded-lg border border-slate-200 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-100"
              />

              <div className="flex flex-col items-center gap-2">
                <Button type="button" variant="ghost" size="icon" onClick={toggleSpeechInput} title={isListening ? 'Stop listening' : 'Start voice input'}>
                  {isListening ? <MicOff className="w-4 h-4"/> : <Mic className="w-4 h-4"/>}
                </Button>

                <Button type="button" variant={speechOutputEnabled ? 'default' : 'outline'} size="icon" onClick={toggleSpeechOutput} title={speechOutputEnabled ? 'Disable speech output' : 'Enable speech output'}>
                  <Volume2 className="w-4 h-4" />
                </Button>

                <Button type="button" onClick={sendMessage} disabled={isSending || !input.trim()} className="h-10 w-10 sm:w-auto sm:px-3">
                  {isSending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                </Button>
              </div>
            </div>
          </div>
        </main>

        {/* Right column: AI avatar and context */}
        <aside className="md:col-span-3 bg-white rounded-2xl shadow-sm p-4 flex flex-col gap-4">
          <div className="flex items-center justify-center">
            <AIDoctorAvatar
              avatar={selectedAvatar || 'female'}
              isSpeaking={isSpeaking}
              isListening={isListening}
              speechEnabled={speechOutputEnabled}
              onSpeechToggle={() => setSpeechOutputEnabled(!speechOutputEnabled)}
            />
          </div>

          <div className="space-y-2">
            <h4 className="text-sm font-semibold">Quick Tips</h4>
            <ul className="text-xs text-slate-500 space-y-1">
              <li>• Provide symptoms, duration and severity.</li>
              <li>• Upload images when relevant.</li>
              <li>• Use clear short sentences (use Enter for newline).</li>
            </ul>
          </div>

          <div className="mt-auto text-xs text-slate-400">Responses are informational and not a substitute for professional medical advice.</div>
        </aside>
      </div>
    </div>
  )
}
