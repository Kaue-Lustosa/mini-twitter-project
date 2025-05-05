"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { Link, useLocation } from "react-router-dom"
import api from "../api"
import "./Search.css"

interface User {
  id: number
  username: string
  profile_picture: string
}

interface Post {
  id: number
  content: string
  user: User
  created_at: string
}

interface Hashtag {
  name: string
}

const Search: React.FC = () => {
  const [query, setQuery] = useState<string>("")
  const [posts, setPosts] = useState<Post[]>([])
  const [users, setUsers] = useState<User[]>([])
  const [hashtags, setHashtags] = useState<Hashtag[]>([])
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string>("")
  const location = useLocation()

  useEffect(() => {
    const searchParams = new URLSearchParams(location.search)
    const q = searchParams.get("q") || ""
    setQuery(q)
    fetchSearchResults()
  }, [location.search])

  const fetchSearchResults = async () => {
    if (!query) {
      setLoading(false)
      return
    }

    try {
      setLoading(true)
      const response = await api.get(`/api/posts/search/?q=${encodeURIComponent(query)}`)
      setPosts(response.data.posts)
      setUsers(response.data.users)
      setHashtags(response.data.hashtags || [])
      setError("")
    } catch (error) {
      console.error("Error searching:", error)
      setError("Failed to fetch search results. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="search-page">
      <h1>Search Results</h1>
      {error && <div className="error-message">{error}</div>}
      {loading && <div className="loading-message">Loading...</div>}

      {users.length > 0 && (
        <div className="users-section">
          <h2>Users</h2>
          <div className="users-list">
            {users.map((user) => (
              <Link to={`/profile/${user.username}`} key={user.id} className="user-card">
                <img src={user.profile_picture || "/placeholder.svg"} alt={user.username} />
                <p>{user.username}</p>
              </Link>
            ))}
          </div>
        </div>
      )}

      {hashtags.length > 0 && (
        <div className="hashtags-section">
          <h2>Hashtags</h2>
          <div className="hashtags-list">
            {hashtags.map((hashtag, index) => (
              <Link to={`/search?q=%23${hashtag.name}`} key={index} className="hashtag-card">
                #{hashtag.name}
              </Link>
            ))}
          </div>
        </div>
      )}

      {posts.length > 0 && (
        <div className="posts-section">
          <h2>Posts</h2>
          <div className="posts-list">
            {posts.map((post) => (
              <div key={post.id} className="post-card">
                <Link to={`/profile/${post.user.username}`}>
                  <img src={post.user.profile_picture || "/placeholder.svg"} alt={post.user.username} />
                  <p>{post.user.username}</p>
                </Link>
                <p>{post.content}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {posts.length === 0 && users.length === 0 && hashtags.length === 0 && !loading && query && (
        <div className="no-results">No results found for "{query}"</div>
      )}
    </div>
  )
}

export default Search
