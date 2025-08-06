"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { User, Mail, Globe, Calendar, Save, Loader2 } from "lucide-react"
import { useAuth } from "@/hooks/use-auth"
import { apiClient } from "@/lib/api"

interface UserAnalytics {
  average_processing_time: number
  model_usage: Record<string, number>
  daily_activity: Record<string, number>
}

export function UserProfile() {
  const { user, refreshUser } = useAuth()
  const [isEditing, setIsEditing] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [analytics, setAnalytics] = useState<UserAnalytics | null>(null)
  const [formData, setFormData] = useState({
    full_name: "",
    preferred_language: "en",
  })

  useEffect(() => {
    if (user) {
      setFormData({
        full_name: user.full_name || "",
        preferred_language: user.preferred_language || "en",
      })
      loadAnalytics()
    }
  }, [user])

  const loadAnalytics = async () => {
    try {
      const response = await apiClient.request("/logs/analytics")
      if (response.data) {
        setAnalytics(response.data)
      }
    } catch (error) {
      console.error("Failed to load analytics:", error)
    }
  }

  const handleSave = async () => {
    if (!user) return

    setIsSaving(true)
    try {
      const response = await apiClient.request("/user/profile", {
        method: "PUT",
        body: JSON.stringify(formData),
      })

      if (response.data) {
        await refreshUser()
        setIsEditing(false)
      }
    } catch (error) {
      console.error("Failed to update profile:", error)
    } finally {
      setIsSaving(false)
    }
  }

  const handleCancel = () => {
    if (user) {
      setFormData({
        full_name: user.full_name || "",
        preferred_language: user.preferred_language || "en",
      })
    }
    setIsEditing(false)
  }

  if (!user) {
    return (
      <div className="text-center py-12">
        <p className="text-lg text-gray-600">Please log in to view your profile.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Profile Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="h-5 w-5" />
            Profile Information
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email Address</Label>
              <div className="flex items-center gap-2">
                <Mail className="h-4 w-4 text-gray-500" />
                <Input id="email" value={user.email} disabled className="bg-gray-50" />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="full_name">Full Name</Label>
              <Input
                id="full_name"
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                disabled={!isEditing}
                placeholder="Enter your full name"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="language">Preferred Language</Label>
              <Select
                value={formData.preferred_language}
                onValueChange={(value) => setFormData({ ...formData, preferred_language: value })}
                disabled={!isEditing}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="en">English</SelectItem>
                  <SelectItem value="ak">Akan</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Account Status</Label>
              <div className="flex items-center gap-2">
                <Badge variant={user.is_active ? "default" : "secondary"}>
                  {user.is_active ? "Active" : "Inactive"}
                </Badge>
              </div>
            </div>

            <div className="space-y-2">
              <Label>Member Since</Label>
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4 text-gray-500" />
                <span className="text-sm">
                  {new Date(user.created_at).toLocaleDateString("en-US", {
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                  })}
                </span>
              </div>
            </div>
          </div>

          <div className="flex gap-2 pt-4">
            {!isEditing ? (
              <Button onClick={() => setIsEditing(true)}>Edit Profile</Button>
            ) : (
              <>
                <Button onClick={handleSave} disabled={isSaving}>
                  {isSaving ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin mr-2" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Save className="h-4 w-4 mr-2" />
                      Save Changes
                    </>
                  )}
                </Button>
                <Button variant="outline" onClick={handleCancel} disabled={isSaving}>
                  Cancel
                </Button>
              </>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Analytics */}
      {analytics && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Globe className="h-5 w-5" />
              Usage Analytics
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <p className="text-sm text-gray-600">Average Response Time</p>
                <p className="text-2xl font-bold text-blue-600">{analytics.average_processing_time.toFixed(2)}s</p>
              </div>

              <div className="text-center p-4 bg-green-50 rounded-lg">
                <p className="text-sm text-gray-600">Most Used Model</p>
                <p className="text-lg font-semibold text-green-600">
                  {Object.entries(analytics.model_usage).sort(([, a], [, b]) => b - a)[0]?.[0] || "N/A"}
                </p>
              </div>

              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <p className="text-sm text-gray-600">Daily Queries (Avg)</p>
                <p className="text-2xl font-bold text-purple-600">
                  {Object.values(analytics.daily_activity).length > 0
                    ? Math.round(
                        Object.values(analytics.daily_activity).reduce((a, b) => a + b, 0) /
                          Object.values(analytics.daily_activity).length,
                      )
                    : 0}
                </p>
              </div>
            </div>

            {/* Model Usage Breakdown */}
            <div className="mt-6">
              <h4 className="text-sm font-medium text-gray-700 mb-3">Model Usage Breakdown</h4>
              <div className="space-y-2">
                {Object.entries(analytics.model_usage).map(([model, count]) => (
                  <div key={model} className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">{model}</span>
                    <Badge variant="outline">{count} queries</Badge>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
