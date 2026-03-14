import axios from "axios"
import { env } from "../config/env"

const { authApiBaseUrl, apiBaseUrl } = env

export const baseClient = axios.create({
  baseURL: apiBaseUrl,
})

export const authClient = axios.create({
  baseURL: authApiBaseUrl,
})
