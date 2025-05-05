"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { useAuth } from "../contexts/AuthContext"
import { Link } from "react-router-dom"
import api from "../services/api"
import { Button } from "../components/ui/button"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "../components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs"
import { Sidebar, SidebarContent, SidebarFooter, SidebarHeader, SidebarProvider } from "../components/ui/sidebar"
import { Avatar, AvatarFallback, AvatarImage } from "../components/ui/avatar"
import { Input } from "../components/ui/input"
import { Textarea } from "../components/ui/textarea"
import { Badge } from "../components/ui/badge"
import { Bell, Home, MessageSquare, Search, Settings, User, Users } from "lucide-react"
import PostCard from "../components/PostCard"

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

export default function HomePage() {
  const { user } = useAuth()
  const [posts, setPosts] = useState<Post[]>([])
  const [trendingTopics, setTrendingTopics] = useState<string[]>([])
  const [suggestedUsers, setSuggestedUsers] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [newPostContent, setNewPostContent] = useState("")
  const [postImage, setPostImage] = useState<File | null>(null)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)

        // Fetch feed posts
        const postsResponse = await api.get("/api/posts/feed/")
        setPosts(postsResponse.data.results)

        // Fetch trending topics (hashtags)
        const trendingResponse = await api.get("/api/posts/trending/")
        setTrendingTopics(trendingResponse.data.slice(0, 5))

        // Fetch suggested users to follow
        const suggestedResponse = await api.get("/api/users/suggested/")
        setSuggestedUsers(suggestedResponse.data.slice(0, 5))
      } catch (error) {
        console.error("Error fetching data:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const handlePostSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!newPostContent.trim()) return

    try {
      setSubmitting(true)

      const formData = new FormData()
      formData.append("content", newPostContent)

      if (postImage) {
        formData.append("image", postImage)
      }

      const response = await api.post("/api/posts/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      })

      // Add new post to the top of the feed
      setPosts((prevPosts) => [response.data, ...prevPosts])

      // Reset form
      setNewPostContent("")
      setPostImage(null)
    } catch (error) {
      console.error("Error creating post:", error)
    } finally {
      setSubmitting(false)
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

  return (
    <SidebarProvider>
      <div className="flex min-h-screen bg-gray-50">
        {/* Sidebar */}
        <Sidebar className="border-r">
          <SidebarHeader className="p-4">
            <div className="flex items-center gap-2">
              <div className="text-2xl font-bold text-blue-600">Mini Twitter</div>
            </div>
          </SidebarHeader>

          <SidebarContent className="px-4 py-2">
            <nav className="space-y-2">
              <Link
                to="/home"
                className="flex items-center gap-3 rounded-md px-3 py-2 text-gray-700 hover:bg-gray-100 bg-gray-100"
              >
                <Home className="h-5 w-5" />
                <span>Início</span>
              </Link>
              <Link
                to="/search"
                className="flex items-center gap-3 rounded-md px-3 py-2 text-gray-700 hover:bg-gray-100"
              >
                <Search className="h-5 w-5" />
                <span>Explorar</span>
              </Link>
              <Link
                to="/notifications"
                className="flex items-center gap-3 rounded-md px-3 py-2 text-gray-700 hover:bg-gray-100"
              >
                <Bell className="h-5 w-5" />
                <span>Notificações</span>
              </Link>
              <Link
                to="/messages"
                className="flex items-center gap-3 rounded-md px-3 py-2 text-gray-700 hover:bg-gray-100"
              >
                <MessageSquare className="h-5 w-5" />
                <span>Mensagens</span>
              </Link>
              <Link
                to={`/profile/${user?.id}`}
                className="flex items-center gap-3 rounded-md px-3 py-2 text-gray-700 hover:bg-gray-100"
              >
                <User className="h-5 w-5" />
                <span>Perfil</span>
              </Link>
              <Link
                to="/following"
                className="flex items-center gap-3 rounded-md px-3 py-2 text-gray-700 hover:bg-gray-100"
              >
                <Users className="h-5 w-5" />
                <span>Seguindo</span>
              </Link>
              <Link
                to="/settings"
                className="flex items-center gap-3 rounded-md px-3 py-2 text-gray-700 hover:bg-gray-100"
              >
                <Settings className="h-5 w-5" />
                <span>Configurações</span>
              </Link>
            </nav>
          </SidebarContent>

          <SidebarFooter className="p-4">
            <div className="flex items-center gap-3">
              <Avatar>
                <AvatarImage src="/placeholder.svg" />
                <AvatarFallback>{user?.username?.[0]?.toUpperCase()}</AvatarFallback>
              </Avatar>
              <div>
                <div className="font-medium">{user?.username}</div>
                <div className="text-xs text-gray-500">@{user?.username}</div>
              </div>
            </div>
          </SidebarFooter>
        </Sidebar>

        {/* Main content */}
        <div className="flex-1">
          <div className="container mx-auto max-w-6xl px-4 py-6">
            <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
              {/* Main feed column */}
              <div className="md:col-span-2 space-y-6">
                {/* New post form */}
                <Card>
                  <CardHeader>
                    <CardTitle>Criar nova postagem</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <form onSubmit={handlePostSubmit}>
                      <div className="space-y-4">
                        <Textarea
                          placeholder="O que está acontecendo?"
                          value={newPostContent}
                          onChange={(e) => setNewPostContent(e.target.value)}
                          className="min-h-[100px]"
                          maxLength={280}
                        />
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <label htmlFor="post-image" className="cursor-pointer text-blue-600 hover:text-blue-800">
                              <span className="flex items-center gap-1">
                                <svg
                                  xmlns="http://www.w3.org/2000/svg"
                                  className="h-5 w-5"
                                  fill="none"
                                  viewBox="0 0 24 24"
                                  stroke="currentColor"
                                >
                                  <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                                  />
                                </svg>
                                {postImage ? "Trocar imagem" : "Adicionar imagem"}
                              </span>
                            </label>
                            <input
                              id="post-image"
                              type="file"
                              accept="image/*"
                              className="hidden"
                              onChange={(e) => e.target.files && setPostImage(e.target.files[0])}
                            />
                            {postImage && <span className="text-sm text-gray-500">{postImage.name}</span>}
                          </div>
                          <div className="text-sm text-gray-500">{newPostContent.length}/280</div>
                        </div>
                      </div>
                    </form>
                  </CardContent>
                  <CardFooter className="flex justify-end">
                    <Button onClick={handlePostSubmit} disabled={!newPostContent.trim() || submitting}>
                      {submitting ? "Publicando..." : "Publicar"}
                    </Button>
                  </CardFooter>
                </Card>

                {/* Feed tabs */}
                <Tabs defaultValue="for-you">
                  <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="for-you">Para você</TabsTrigger>
                    <TabsTrigger value="following">Seguindo</TabsTrigger>
                  </TabsList>

                  <TabsContent value="for-you" className="space-y-4 mt-4">
                    {loading ? (
                      <div className="text-center py-8">Carregando posts...</div>
                    ) : posts.length === 0 ? (
                      <div className="text-center py-8">
                        <p className="text-gray-500">Nenhum post encontrado.</p>
                        <p className="text-gray-500">Siga alguns usuários para ver posts aqui!</p>
                      </div>
                    ) : (
                      posts.map((post) => <PostCard key={post.id} post={post} onLike={handlePostLike} />)
                    )}
                  </TabsContent>

                  <TabsContent value="following" className="space-y-4 mt-4">
                    <div className="text-center py-8">
                      <p className="text-gray-500">Mostrando posts apenas de pessoas que você segue.</p>
                    </div>
                  </TabsContent>
                </Tabs>
              </div>

              {/* Right sidebar */}
              <div className="space-y-6">
                {/* Search */}
                <Card>
                  <CardContent className="pt-6">
                    <div className="relative">
                      <Search className="absolute left-2 top-2.5 h-4 w-4 text-gray-500" />
                      <Input placeholder="Pesquisar no Mini Twitter" className="pl-8" />
                    </div>
                  </CardContent>
                </Card>

                {/* Trending topics */}
                <Card>
                  <CardHeader>
                    <CardTitle>Assuntos do momento</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {trendingTopics.length > 0 ? (
                        trendingTopics.map((topic, index) => (
                          <div key={index} className="flex items-center justify-between">
                            <div>
                              <div className="text-sm text-gray-500">Trending in Brazil</div>
                              <div className="font-medium">#{topic}</div>
                            </div>
                            <Badge variant="outline">{Math.floor(Math.random() * 10000)}+ posts</Badge>
                          </div>
                        ))
                      ) : (
                        <div className="text-center py-2">
                          <p className="text-gray-500">Nenhum tópico em alta no momento.</p>
                        </div>
                      )}
                    </div>
                  </CardContent>
                  <CardFooter>
                    <Link to="/explore/trending" className="text-sm text-blue-600 hover:underline">
                      Mostrar mais
                    </Link>
                  </CardFooter>
                </Card>

                {/* Who to follow */}
                <Card>
                  <CardHeader>
                    <CardTitle>Quem seguir</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {suggestedUsers.length > 0 ? (
                        suggestedUsers.map((suggestedUser, index) => (
                          <div key={index} className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <Avatar>
                                <AvatarImage src={suggestedUser.avatar || "/placeholder.svg"} />
                                <AvatarFallback>{suggestedUser.username[0].toUpperCase()}</AvatarFallback>
                              </Avatar>
                              <div>
                                <div className="font-medium">{suggestedUser.username}</div>
                                <div className="text-xs text-gray-500">@{suggestedUser.username}</div>
                              </div>
                            </div>
                            <Button size="sm" variant="outline">
                              Seguir
                            </Button>
                          </div>
                        ))
                      ) : (
                        <div className="text-center py-2">
                          <p className="text-gray-500">Nenhuma sugestão disponível.</p>
                        </div>
                      )}
                    </div>
                  </CardContent>
                  <CardFooter>
                    <Link to="/explore/users" className="text-sm text-blue-600 hover:underline">
                      Mostrar mais
                    </Link>
                  </CardFooter>
                </Card>
              </div>
            </div>
          </div>
        </div>
      </div>
    </SidebarProvider>
  )
}