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
