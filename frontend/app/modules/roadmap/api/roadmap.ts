import { baseClient } from "~/shared/api/axios-client"

export type ProgressItem = {
  roadmap_key: string
  step_id: string
}

export async function getProgress(roadmapKey?: string): Promise<ProgressItem[]> {
  const params: Record<string, string> = {}
  if (roadmapKey) params.roadmap_key = roadmapKey
  const { data } = await baseClient.get<ProgressItem[]>("/api/roadmap/progress", { params })
  return data
}

export async function toggleProgress(roadmapKey: string, stepId: string): Promise<{ action: string }> {
  const { data } = await baseClient.post<{ action: string }>("/api/roadmap/progress", {
    roadmap_key: roadmapKey,
    step_id: stepId,
  })
  return data
}

export type RoadmapStep = {
  id: string
  title: string
  description: string
  details: string
  resources: string[]
  skills: string[]
  duration: string
}

export type PersonalRoadmap = {
  title: string
  description: string | null
  steps: RoadmapStep[]
}

export async function getPersonalRoadmap(): Promise<PersonalRoadmap | null> {
  const { data } = await baseClient.get<PersonalRoadmap | null>("/api/roadmap/personal")
  return data
}

export async function savePersonalRoadmap(roadmap: { title: string; description?: string; steps: RoadmapStep[] }): Promise<PersonalRoadmap> {
  const { data } = await baseClient.put<PersonalRoadmap>("/api/roadmap/personal", roadmap)
  return data
}

export async function deletePersonalRoadmap(): Promise<void> {
  await baseClient.delete("/api/roadmap/personal")
}
