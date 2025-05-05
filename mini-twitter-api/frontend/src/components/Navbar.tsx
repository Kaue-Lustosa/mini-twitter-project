"use client"

import type React from "react"
import { Link, useNavigate } from "react-router-dom"
import { useAuth } from "../contexts/AuthContext"
import { useSettings } from "../contexts/SettingsContext"
import "./Navbar.css"
import SearchBar from "./SearchBar"
import NotificationBell from "./NotificationBell"

const Navbar: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuth()
  const { settings } = useSettings()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate("/login")
  }

  return (
    <nav className="navbar">
      <div className="container">
        <Link to="/" className="navbar-brand">
          {settings.project_name}
        </Link>

        <div className="navbar-menu">
          {isAuthenticated ? (
            <>
              <SearchBar />
              <Link to="/" className="navbar-item">
                Feed
              </Link>
              <Link to={`/profile/${user?.id}`} className="navbar-item">
                Profile
              </Link>
              <NotificationBell />
              <button onClick={handleLogout} className="navbar-item logout-btn">
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="navbar-item">
                Login
              </Link>
              <Link to="/register" className="navbar-item">
                Register
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}

export default Navbar