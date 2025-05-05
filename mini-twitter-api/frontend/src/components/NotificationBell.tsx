"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { useAuth } from "../contexts/AuthContext"
import "./NotificationBell.css"

interface Notification {
  id: number
  sender: {
    id: number
    username: string
  }
  notification_type: string
  text: string
  is_read: boolean
  created_at: string
}

const NotificationBell: React.FC = () => {
  const { user, isAuthenticated } = useAuth()
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [unreadCount, setUnreadCount] = useState<number>(0)
  const [showDropdown, setShowDropdown] = useState<boolean>(false)
  const [socket, setSocket] = useState<WebSocket | null>(null)

  useEffect(() => {
    if (isAuthenticated) {
      // Fetch notifications
      fetchNotifications()

      // Get JWT token
      const token = localStorage.getItem("token")

      // Set up WebSocket connection with token
      const ws = new WebSocket(`ws://${window.location.hostname}:8001/ws/notifications/?token=${token}`)

      ws.onopen = () => {
        console.log("WebSocket connection established")
        // Request unread count
        ws.send(JSON.stringify({ message: "get_unread_count" }))
      }

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)

        if (data.type === "notification") {
          // Add new notification to the list
          setNotifications((prev) => [data.notification, ...prev])
          // Increment unread count
          setUnreadCount((prev) => prev + 1)
        } else if (data.type === "unread_count") {
          // Update unread count
          setUnreadCount(data.count)
        }
      }

      ws.onerror = (error) => {
        console.error("WebSocket error:", error)
      }

      ws.onclose = () => {
        console.log("WebSocket connection closed")
      }

      setSocket(ws)

      // Clean up WebSocket connection
      return () => {
        if (ws) {
          ws.close()
        }
      }
    }
  }, [isAuthenticated])

  const fetchNotifications = async () => {
    try {
      const response = await fetch("/api/notifications/")
      const data = await response.json()
      setNotifications(data.results || data)
      setUnreadCount(data.results?.filter((n: Notification) => !n.is_read).length || 0)
    } catch (error) {
      console.error("Error fetching notifications:", error)
    }
  }

  const markAsRead = async (id: number) => {
    try {
      await fetch(`/api/notifications/${id}/mark_as_read/`, {
        method: "POST",
      })

      // Update local state
      setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, is_read: true } : n)))
      setUnreadCount((prev) => Math.max(0, prev - 1))
    } catch (error) {
      console.error("Error marking notification as read:", error)
    }
  }

  const markAllAsRead = async () => {
    try {
      await fetch("/api/notifications/mark_all_as_read/", {
        method: "POST",
      })

      // Update local state
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })))
      setUnreadCount(0)
    } catch (error) {
      console.error("Error marking all notifications as read:", error)
    }
  }

  const toggleDropdown = () => {
    setShowDropdown(!showDropdown)
  }

  if (!isAuthenticated) {
    return null
  }

  return (
    <div className="notification-bell">
      <button className="bell-button" onClick={toggleDropdown}>
        🔔{unreadCount > 0 && <span className="unread-count">{unreadCount}</span>}
      </button>

      {showDropdown && (
        <div className="notification-dropdown">
          <div className="notification-header">
            <h3>Notifications</h3>
            {unreadCount > 0 && (
              <button className="mark-all-read" onClick={markAllAsRead}>
                Mark all as read
              </button>
            )}
          </div>

          <div className="notification-list">
            {notifications.length === 0 ? (
              <p className="no-notifications">No notifications yet</p>
            ) : (
              notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`notification-item ${!notification.is_read ? "unread" : ""}`}
                  onClick={() => markAsRead(notification.id)}
                >
                  <p className="notification-text">{notification.text}</p>
                  <span className="notification-time">{new Date(notification.created_at).toLocaleTimeString()}</span>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default NotificationBell
