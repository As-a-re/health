"use client"

import { createContext, useContext, useEffect, useState, type ReactNode } from "react"
import { api } from "@/lib/api"

interface User {
  id: string
  email: string
  full_name?: string
  preferred_language: string
  is_active: boolean
  created_at?: string
}

interface AuthError {
  title: string;
  message: string;
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<{ success: boolean; error?: AuthError }>
  register: (userData: {
    email: string
    password: string
    full_name: string
    preferred_language?: string
  }) => Promise<{ success: boolean; error?: AuthError }>
  logout: () => void
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<AuthError | null>(null)

  const isAuthenticated = !!user

  // Check for existing session on mount
  useEffect(() => {
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        setIsLoading(false);
        return;
      }

      const result = await api.getCurrentUser();
      if (result.data) {
        setUser(result.data);
      } else {
        // Clear invalid token
        localStorage.removeItem('auth_token');
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      localStorage.removeItem('auth_token');
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const result = await api.login({ email, password });
      
      if (result.error) {
        setError({
          title: 'Login Failed',
          message: result.error
        });
        return { success: false };
      }
      
      if (result.data?.user) {
        setUser(result.data.user);
        return { success: true };
      }
      
      throw new Error('No user data received');
      
    } catch (err) {
      console.error('Login error:', err);
      setError({
        title: 'Login Error',
        message: err instanceof Error ? err.message : 'An unknown error occurred'
      });
      return { success: false };
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (userData: {
    email: string;
    password: string;
    full_name: string;
    preferred_language?: string;
  }) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await api.register({
        email: userData.email,
        password: userData.password,
        full_name: userData.full_name,
        preferred_language: userData.preferred_language || 'en'
      });

      if (response.data) {
        // Handle successful registration
        if (response.data.access_token) {
          localStorage.setItem('auth_token', response.data.access_token);
          api.setToken(response.data.access_token);
          
          if (response.data.user) {
            setUser(response.data.user);
          } else {
            // If no user data in response, fetch it
            const userResult = await api.getCurrentUser();
            if (userResult.data) {
              setUser(userResult.data);
            }
          }
        }
        return { success: true };
      } else {
        setError({
          title: 'Registration Failed',
          message: response.error || 'Registration failed. Please try again.'
        });
        return { success: false };
      }
    } catch (error) {
      console.error('Registration error:', error);
      setError({
        title: 'Registration Error',
        message: error instanceof Error ? error.message : 'An unknown error occurred'
      });
      return { success: false };
    } finally {
      setIsLoading(false);
    }
  };

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
