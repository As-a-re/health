"use client"

import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Languages } from "lucide-react"

interface LanguageToggleProps {
  currentLanguage: "en" | "ak"
  onLanguageChange: (language: "en" | "ak") => void
}

export function LanguageToggle({ currentLanguage, onLanguageChange }: LanguageToggleProps) {
  const toggleLanguage = () => {
    onLanguageChange(currentLanguage === "en" ? "ak" : "en")
  }

  return (
    <div className="flex items-center gap-2">
      <Button variant="outline" size="sm" onClick={toggleLanguage} className="flex items-center gap-2 bg-transparent">
        <Languages className="h-4 w-4" />
        <span className="text-sm">{currentLanguage === "en" ? "English" : "Akan"}</span>
      </Button>
      <Badge variant={currentLanguage === "en" ? "default" : "secondary"}>
        {currentLanguage === "en" ? "EN" : "AK"}
      </Badge>
    </div>
  )
}
