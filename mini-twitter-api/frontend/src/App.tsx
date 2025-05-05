"use client"

import type React from "react"
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom"
import { AuthProvider, useAuth } from "./contexts/AuthContext"
import { SettingsProvider } from "./contexts/SettingsContext"
import LoginPage from "./pages/LoginPage"
import Register from "./pages/Register"
import HomePage from "./pages/HomePage"
import Profile from "./pages/Profile"
import Search from "./pages/Search"
import "./App.css"

const PrivateRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Carregando...</div>
  }

  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />
}

const App: React.FC = () => {
  return (
    <AuthProvider>
      <SettingsProvider>
        <Router>
          <div className="app">
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<Register />} />
              <Route
                path="/"
                element={
                  <PrivateRoute>
                    <Navigate to="/home" />
                  </PrivateRoute>
                }
              />
              <Route
                path="/home"
                element={
                  <PrivateRoute>
                    <HomePage />
                  </PrivateRoute>
                }
              />
              <Route
                path="/profile/:userId"
                element={
                  <PrivateRoute>
                    <Profile />
                  </PrivateRoute>
                }
              />
              <Route
                path="/search"
                element={
                  <PrivateRoute>
                    <Search />
                  </PrivateRoute>
                }
              />
            </Routes>
          </div>
        </Router>
      </SettingsProvider>
    </AuthProvider>
  )
}

export default App
