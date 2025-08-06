"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Trash2, Calendar, MessageSquare, TrendingUp, User, Activity } from "lucide-react"
import { apiClient } from "@/lib/api"
import { useAuth } from "@/hooks/use-auth"

interface HealthQuery {
  id: string
  query_text: string
  query_language: string
  response_text: string
  response_language: string
  confidence_score: string
  model_used: string
  created_at: string
}

interface UserStats {
  total_queries: number
  recent_queries: number
  language_breakdown: Record<string, number>
  member_since: string
}

export function HealthRecords() {
  const { user } = useAuth()
  const [queries, setQueries] = useState<HealthQuery[]>([])
  const [stats, setStats] = useState<UserStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)

  useEffect(() => {
    if (user) {
      loadHealthRecords()
      loadUserStats()
    }
  }, [user, currentPage])

  const loadHealthRecords = async () => {
    try {
      const response = await apiClient.getUserHistory(currentPage, 10)
      if (response.data) {
        setQueries(response.data.queries)
        setTotalPages(response.data.total_pages)
      }
    } catch (error) {
      console.error("Failed to load health records:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const loadUserStats = async () => {
    try {
      const response = await apiClient.request("/user/stats")
      if (response.data) {
        setStats(response.data)
      }
    } catch (error) {
      console.error("Failed to load user stats:", error)
    }
  }

  const deleteQuery = async (queryId: string) => {
    try {
      const response = await apiClient.request(`/user/history/${queryId}`, {
        method: "DELETE",
      })

      if (response.data) {
        setQueries(queries.filter((q) => q.id !== queryId))
        // Reload stats
        loadUserStats()
      }
    } catch (error) {
      console.error("Failed to delete query:", error)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  if (!user) {
    return (
      <div className="text-center py-12">
        <p className="text-lg text-gray-600">Please log in to view your health records.</p>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="text-center py-12">
        <p className="text-lg text-gray-600">Loading your health records...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* User Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5 text-blue-600" />
                <div>
                  <p className="text-sm text-gray-600">Total Queries</p>
                  <p className="text-2xl font-bold">{stats.total_queries}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <Activity className="h-5 w-5 text-green-600" />
                <div>
                  <p className="text-sm text-gray-600">Recent (30 days)</p>
                  <p className="text-2xl font-bold">{stats.recent_queries}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-purple-600" />
                <div>
                  <p className="text-sm text-gray-600">Languages Used</p>
                  <p className="text-2xl font-bold">{Object.keys(stats.language_breakdown).length}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <User className="h-5 w-5 text-orange-600" />
                <div>
                  <p className="text-sm text-gray-600">Member Since</p>
                  <p className="text-sm font-semibold">{new Date(stats.member_since).toLocaleDateString()}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Health Records */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            Your Health Query History
          </CardTitle>
        </CardHeader>
        <CardContent>
          {queries.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-600">No health queries yet. Start a conversation with your AI doctor!</p>
            </div>
          ) : (
            <div className="space-y-4">
              {queries.map((query) => (
                <div key={query.id} className="border rounded-lg p-4 space-y-3">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant="outline">{query.query_language === "en" ? "English" : "Akan"}</Badge>
                        <Badge variant="secondary">
                          {Math.round(Number.parseFloat(query.confidence_score || "0") * 100)}% confidence
                        </Badge>
                        <Badge variant="outline" className="text-xs">
                          {query.model_used}
                        </Badge>
                        <span className="text-sm text-gray-500">{formatDate(query.created_at)}</span>
                      </div>

                      <div className="space-y-2">
                        <div>
                          <p className="text-sm font-medium text-gray-700">Your Question:</p>
                          <p className="text-sm bg-blue-50 p-2 rounded">{query.query_text}</p>
                        </div>

                        <div>
                          <p className="text-sm font-medium text-gray-700">AI Response:</p>
                          <p className="text-sm bg-gray-50 p-2 rounded">{query.response_text}</p>
                        </div>
                      </div>
                    </div>

                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => deleteQuery(query.id)}
                      className="text-red-600 hover:text-red-800 hover:bg-red-50"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex justify-center gap-2 mt-6">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                    disabled={currentPage === 1}
                  >
                    Previous
                  </Button>

                  <span className="flex items-center px-3 text-sm">
                    Page {currentPage} of {totalPages}
                  </span>

                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                    disabled={currentPage === totalPages}
                  >
                    Next
                  </Button>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
