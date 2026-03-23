import axios from "axios"
import { env } from "../config/env"

const { apiBaseUrl } = env

export const baseClient = axios.create({
  baseURL: apiBaseUrl,
})

baseClient.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    try {
      const raw = window.localStorage.getItem("auth")
      if (raw) {
        const { token } = JSON.parse(raw)
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
      }
    } catch {}
  }
  return config
})

baseClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("auth")
      window.location.href = "/sign-in"
    }
    return Promise.reject(error)
  }
)
