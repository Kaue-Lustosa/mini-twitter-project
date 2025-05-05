"use client"

import type React from "react"
import { createContext, useState, useContext, useEffect } from "react"
import api from "../services/api"

interface AppSettings {
  project_name: string
  version: string
  theme?: string
  features?: string[]
  [key: string]: unknown
}

interface SettingsContextType {
  settings: AppSettings
  loading: boolean
  error: string | null
  refreshSettings: () => Promise<void>
}

const defaultSettings: AppSettings = {
  project_name: "Mini Twitter",
  version: "1.0.0",
}

const SettingsContext = createContext<SettingsContextType>({
  settings: defaultSettings,
  loading: true,
  error: null,
  refreshSettings: async () => {},
})

export const useSettings = () => useContext(SettingsContext)

export const SettingsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [settings, setSettings] = useState<AppSettings>(defaultSettings)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchSettings = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await api.get("/api/settings/")
      setSettings(response.data)
    } catch (error) {
      console.error("Error fetching app settings:", error)
      setError("Failed to load application settings")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchSettings()
  }, [])

  const refreshSettings = async () => {
    await fetchSettings()
  }

  return (
    <SettingsContext.Provider
      value={{
        settings,
        loading,
        error,
        refreshSettings,
      }}
    >
      {children}
    </SettingsContext.Provider>
  )
}