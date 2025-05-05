import axios from "axios"

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || "http://localhost:8000",
})

// Add a response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // If the error is 401 and we haven't tried to refresh the token yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem("refreshToken")

        if (!refreshToken) {
          throw new Error("No refresh token available")
        }

        const response = await axios.post(
          `${process.env.REACT_APP_API_URL || "http://localhost:8000"}/api/users/token/refresh/`,
          {
            refresh: refreshToken,
          },
        )

        const { access } = response.data

        localStorage.setItem("token", access)
        api.defaults.headers.common["Authorization"] = `Bearer ${access}`

        return api(originalRequest)
      } catch (refreshError) {
        // If refresh fails, log the user out
        localStorage.removeItem("token")
        localStorage.removeItem("refreshToken")
        delete api.defaults.headers.common["Authorization"]
        window.location.href = "/login"
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  },
)

export default api
