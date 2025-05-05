"use client"

import type React from "react"
import { useState } from "react"
import api from "../services/api"
import "./PostForm.css"

interface PostFormProps {
  onPostCreated: (post: any) => void
}

const PostForm: React.FC<PostFormProps> = ({ onPostCreated }) => {
  const [content, setContent] = useState("")
  const [image, setImage] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!content.trim()) {
      setError("Post content cannot be empty")
      return
    }

    try {
      setLoading(true)
      setError("")

      const formData = new FormData()
      formData.append("content", content)

      if (image) {
        formData.append("image", image)
      }

      const response = await api.post("/api/posts/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      })

      setContent("")
      setImage(null)
      onPostCreated(response.data)
    } catch (error) {
      console.error("Error creating post:", error)
      setError("Failed to create post. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setImage(e.target.files[0])
    }
  }

  return (
    <div className="post-form-container">
      <h2>Create a Post</h2>
      <form className="post-form" onSubmit={handleSubmit}>
        <textarea
          placeholder="What's on your mind?"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          maxLength={280}
          disabled={loading}
        />

        <div className="form-actions">
          <div className="image-upload">
            <label htmlFor="image-input">📷 {image ? "Change Image" : "Add Image"}</label>
            <input id="image-input" type="file" accept="image/*" onChange={handleImageChange} disabled={loading} />
          </div>

          {image && (
            <div className="image-preview">
              <span className="image-name">{image.name}</span>
              <button type="button" className="remove-image" onClick={() => setImage(null)} disabled={loading}>
                ✖
              </button>
            </div>
          )}

          <button type="submit" className="post-button" disabled={loading}>
            {loading ? "Posting..." : "Post"}
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}
      </form>
    </div>
  )
}

export default PostForm
