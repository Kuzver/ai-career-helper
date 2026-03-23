import { baseClient } from "~/shared/api/axios-client"

export type ProfileData = {
  name: string | null
  specialization: string | null
  experience_level: string | null
  skills: string | null
  career_goal: string | null
}

export async function getProfile(): Promise<ProfileData> {
  const { data } = await baseClient.get<ProfileData>("/api/profile")
  return data
}

export async function updateProfile(profile: {
  name?: string | null
  specialization?: string | null
  experience_level?: string | null
  skills?: string | null
  career_goal?: string | null
}): Promise<ProfileData> {
  const { data } = await baseClient.put<ProfileData>("/api/profile", profile)
  return data
}
