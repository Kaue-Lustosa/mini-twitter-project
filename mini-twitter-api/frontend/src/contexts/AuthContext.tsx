"use client"

import type React from "react"
import { createContext, useState, useContext, useEffect } from "react"
import api from "../services/api"

interface User {
  id: number
  username: string
  email: string
}

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  loading: boolean
  login: (username: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  isAuthenticated: false,
  loading: true,
  login: async () => {},
  register: async () => {},
  logout: () => {},
})

export const useAuth = () => useContext(AuthContext)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadUser = async () => {
      const token = localStorage.getItem("token")

      if (token) {
        api.defaults.headers.common["Authorization"] = `Bearer ${token}`

        try {
          const response = await api.get("/api/users/me/")
          setUser(response.data)
        } catch (error) {
          localStorage.removeItem("token")
          delete api.defaults.headers.common["Authorization"]
        }
      }

      setLoading(false)
    }

    loadUser()
  }, [])

  const login = async (username: string, password: string) => {
    const response = await api.post("/api/users/token/", { username, password })
    const { access, refresh } = response.data

    localStorage.setItem("token", access)
    localStorage.setItem("refreshToken", refresh)

    api.defaults.headers.common["Authorization"] = `Bearer ${access}`

    const userResponse = await api.get("/api/users/me/")
    setUser(userResponse.data)
  }

  const register = async (username: string, email: string, password: string) => {
    await api.post("/api/users/", { username, email, password })
    await login(username, password)
  }

  const logout = () => {
    localStorage.removeItem("token")
    localStorage.removeItem("refreshToken")
    delete api.defaults.headers.common["Authorization"]
    setUser(null)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        loading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}
