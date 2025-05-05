"use client"

import type React from "react"
import { useState, useEffect } from "react"
import api from "../services/api"
import PostForm from "../components/PostForm"
import PostCard from "../components/PostCard"
import "./Feed.css"

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

const Feed: React.FC = () => {
  const [posts, setPosts] = useState<Post[]>([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [hasMore, setHasMore] = useState(true)

  const fetchFeed = async (pageNum = 1) => {
    try {
      setLoading(true)
      const response = await api.get(`/api/posts/feed/?page=${pageNum}`)

      if (pageNum === 1) {
        setPosts(response.data.results)
      } else {
        setPosts((prevPosts) => [...prevPosts, ...response.data.results])
      }

      setHasMore(!!response.data.next)
      setLoading(false)
    } catch (error) {
      console.error("Error fetching feed:", error)
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchFeed()
  }, [])

  const handleLoadMore = () => {
    if (!loading && hasMore) {
      const nextPage = page + 1
      setPage(nextPage)
      fetchFeed(nextPage)
    }
  }

  const handlePostCreated = (newPost: Post) => {
    setPosts((prevPosts) => [newPost, ...prevPosts])
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

  return (
    <div className="feed">
      <h1>Your Feed</h1>
      <PostForm onPostCreated={handlePostCreated} />

      <div className="posts-container">
        {posts.length === 0 && !loading ? (
          <p className="no-posts">No posts yet. Follow some users to see their posts in your feed!</p>
        ) : (
          posts.map((post) => <PostCard key={post.id} post={post} onLike={handlePostLike} />)
        )}

        {loading && <p className="loading">Loading...</p>}

        {!loading && hasMore && (
          <button className="load-more-btn" onClick={handleLoadMore}>
            Load More
          </button>
        )}
      </div>
    </div>
  )
}

export default Feed
