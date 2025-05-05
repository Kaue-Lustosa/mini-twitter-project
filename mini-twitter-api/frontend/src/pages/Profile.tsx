"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { useParams } from "react-router-dom"
import api from "../services/api"
import { useAuth } from "../contexts/AuthContext"
import PostCard from "../components/PostCard"
import "./Profile.css"

interface Profile {
  id: number
  username: string
  email: string
  bio: string
  avatar: string | null
  followers_count: number
  following_count: number
}

interface Post {
  id: number
  user: {
    id: number
    username: string
    email: string
  }
  content: string
  image: string | null
  likes_count: number
  is_liked: boolean
  created_at: string
}

const Profile: React.FC = () => {
  const { userId } = useParams<{ userId: string }>()
  const { user } = useAuth()
  const [profile, setProfile] = useState<Profile | null>(null)
  const [posts, setPosts] = useState<Post[]>([])
  const [loading, setLoading] = useState(true)
  const [isFollowing, setIsFollowing] = useState(false)
  const [page, setPage] = useState(1)
  const [hasMore, setHasMore] = useState(true)

  const isOwnProfile = user?.id === Number(userId)

  const fetchProfile = async () => {
    try {
      const profileResponse = await api.get(`/api/users/profiles/${userId}/`)
      setProfile(profileResponse.data)

      // Check if the current user is following this profile
      if (!isOwnProfile) {
        try {
          await api.get(`/api/users/${userId}/followers/?user_id=${user?.id}`)
          setIsFollowing(true)
        } catch (error) {
          setIsFollowing(false)
        }
      }
    } catch (error) {
      console.error("Error fetching profile:", error)
    }
  }

  const fetchPosts = async (pageNum = 1) => {
    try {
      const postsResponse = await api.get(`/api/posts/?user_id=${userId}&page=${pageNum}`)

      if (pageNum === 1) {
        setPosts(postsResponse.data.results)
      } else {
        setPosts((prevPosts) => [...prevPosts, ...postsResponse.data.results])
      }

      setHasMore(!!postsResponse.data.next)
    } catch (error) {
      console.error("Error fetching posts:", error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    setLoading(true)
    fetchProfile()
    fetchPosts()
  }, [userId])

  const handleFollow = async () => {
    try {
      if (isFollowing) {
        await api.post(`/api/users/${userId}/unfollow/`)
        setIsFollowing(false)
        setProfile((prev) => (prev ? { ...prev, followers_count: prev.followers_count - 1 } : null))
      } else {
        await api.post(`/api/users/${userId}/follow/`)
        setIsFollowing(true)
        setProfile((prev) => (prev ? { ...prev, followers_count: prev.followers_count + 1 } : null))
      }
    } catch (error) {
      console.error("Error following/unfollowing user:", error)
    }
  }

  const handleLoadMore = () => {
    if (!loading && hasMore) {
      const nextPage = page + 1
      setPage(nextPage)
      fetchPosts(nextPage)
    }
  }

  const handlePostLike = async (postId: number) => {
    try {
      const post = posts.find((p) => p.id === postId)

      if (!post) return

      if (post.is_liked) {
        await api.post(`/api/posts/${postId}/unlike/`)
      } else {
        await api.post(`/api/posts/${postId}/like/`)
      }

      setPosts((prevPosts) =>
        prevPosts.map((p) =>
          p.id === postId
            ? {
                ...p,
                is_liked: !p.is_liked,
                likes_count: p.is_liked ? p.likes_count - 1 : p.likes_count + 1,
              }
            : p,
        ),
      )
    } catch (error) {
      console.error("Error liking/unliking post:", error)
    }
  }

  if (loading && !profile) {
    return <div className="loading">Loading profile...</div>
  }

  if (!profile) {
    return <div className="error">Profile not found</div>
  }

  return (
    <div className="profile-container">
      <div className="profile-header">
        <div className="profile-info">
          {profile.avatar ? (
            <img src={profile.avatar || "/placeholder.svg"} alt={profile.username} className="profile-avatar" />
          ) : (
            <div className="profile-avatar-placeholder">{profile.username[0]}</div>
          )}

          <div className="profile-details">
            <h1 className="profile-username">{profile.username}</h1>
            <p className="profile-bio">{profile.bio || "No bio yet"}</p>

            <div className="profile-stats">
              <div className="stat">
                <span className="stat-count">{posts.length}</span>
                <span className="stat-label">Posts</span>
              </div>
              <div className="stat">
                <span className="stat-count">{profile.followers_count}</span>
                <span className="stat-label">Followers</span>
              </div>
              <div className="stat">
                <span className="stat-count">{profile.following_count}</span>
                <span className="stat-label">Following</span>
              </div>
            </div>
          </div>
        </div>

        {!isOwnProfile && (
          <button className={`follow-button ${isFollowing ? "following" : ""}`} onClick={handleFollow}>
            {isFollowing ? "Unfollow" : "Follow"}
          </button>
        )}
      </div>

      <div className="profile-posts">
        <h2>Posts</h2>

        {posts.length === 0 && !loading ? (
          <p className="no-posts">No posts yet</p>
        ) : (
          <div className="posts-container">
            {posts.map((post) => (
              <PostCard key={post.id} post={post} onLike={handlePostLike} />
            ))}

            {loading && <p className="loading">Loading posts...</p>}

            {!loading && hasMore && (
              <button className="load-more-btn" onClick={handleLoadMore}>
                Load More
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default Profile
