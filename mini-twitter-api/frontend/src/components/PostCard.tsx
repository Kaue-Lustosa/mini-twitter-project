"use client"

import type React from "react"
import { Link } from "react-router-dom"
import { formatDistanceToNow } from "date-fns"
import "./PostCard.css"

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

interface PostCardProps {
  post: Post
  onLike: (postId: number) => void
}

const PostCard: React.FC<PostCardProps> = ({ post, onLike }) => {
  const { id, user, content, image, likes_count, is_liked, created_at } = post

  const renderContentWithHashtags = (content: string) => {
    // Regular expression to find hashtags
    const hashtagRegex = /#(\w+)/g

    // Split the content by hashtags
    const parts = content.split(hashtagRegex)

    // Render each part, making hashtags clickable
    return parts.map((part, index) => {
      // Even indices are regular text, odd indices are hashtags
      if (index % 2 === 0) {
        return part
      } else {
        // This is a hashtag
        return (
          <Link key={index} to={`/search?q=%23${part}`} className="hashtag">
            #{part}
          </Link>
        )
      }
    })
  }

  return (
    <div className="post-card">
      <div className="post-header">
        <Link to={`/profile/${user.id}`} className="user-link">
          <span className="username">{user.username}</span>
        </Link>
        <span className="timestamp">{formatDistanceToNow(new Date(created_at), { addSuffix: true })}</span>
      </div>

      <div className="post-content">{renderContentWithHashtags(content)}</div>

      {image && (
        <div className="post-image">
          <img src={image || "/placeholder.svg"} alt="Post" />
        </div>
      )}

      <div className="post-actions">
        <button className={`like-button ${is_liked ? "liked" : ""}`} onClick={() => onLike(id)}>
          {is_liked ? "❤️" : "🤍"} {likes_count}
        </button>
      </div>
    </div>
  )
}

export default PostCard
