import axios from "axios"
import { env } from "../config/env"

const { apiBaseUrl } = env

export const baseClient = axios.create({
  baseURL: apiBaseUrl,
})

// Add JWT token to every request
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
