"use client"

import { createContext, useContext, useEffect, useState, type ReactNode } from "react"
import { api } from "@/lib/api"

interface User {
  id: string
  email: string
  full_name?: string
  preferred_language: string
  is_active: boolean
  created_at: string
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>
  register: (userData: {
    email: string
    password: string
    full_name?: string
    preferred_language?: string
  }) => Promise<{ success: boolean; error?: string }>
  logout: () => void
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const isAuthenticated = !!user

  // Check for existing session on mount
  useEffect(() => {
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem("auth_token")
      if (!token) {
        setIsLoading(false)
        return
      }

      const response = await api.getCurrentUser()
      if (response.data) {
        setUser(response.data as User)
      } else {
        // Invalid token, clear it
        localStorage.removeItem("auth_token")
      }
    } catch (error) {
      console.error("Auth check failed:", error)
      localStorage.removeItem("auth_token")
    } finally {
      setIsLoading(false)
    }
  }

  const login = async (email: string, password: string) => {
    try {
      console.log('Attempting login with email:', { email }) // Debug log
      const response = await api.login({ email, password })
      console.log('API login response:', response) // Debug log

      if (response.data) {
        console.log('Login successful, user data:', response.data.user) // Debug log
        setUser(response.data.user)
        return { success: true }
      } else {
        console.error('Login failed, error:', response.error) // Debug log
        return { 
          success: false, 
          error: response.error || "Login failed. Please check your credentials and try again." 
        }
      }
    } catch (error) {
      console.error('Login error caught:', error) // Debug log
      const errorMessage = error instanceof Error ? error.message : 'Failed to connect to server'
      return { 
        success: false, 
        error: errorMessage.includes('401') 
          ? 'Invalid email or password' 
          : `Login failed: ${errorMessage}` 
      }
    }
  }

  const register = async (userData: {
    email: string
    password: string
    full_name?: string
    preferred_language?: string
  }) => {
    try {
      const response = await api.register({
        email: userData.email,
        password: userData.password,
        full_name: userData.full_name,
        preferred_language: userData.preferred_language || 'en'
      })

      if (response.data) {
        setUser(response.data.user)
        return { success: true }
      } else {
        return { success: false, error: response.error || "Registration failed" }
      }
    } catch (error) {
      return { success: false, error: "Registration failed. Please try again." }
    }
  }

  const logout = () => {
    api.logout()
    setUser(null)
  }

  const refreshUser = async () => {
    try {
      const response = await api.getCurrentUser()
      if (response.data) {
        setUser(response.data as User)
      }
    } catch (error) {
      console.error("Failed to refresh user:", error)
    }
  }

  const value = {
    user,
    isLoading,
    isAuthenticated,
    login,
    register,
    logout,
    refreshUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
