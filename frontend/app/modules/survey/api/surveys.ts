import { baseClient } from "~/shared/api/axios-client"

export type SurveyListItem = {
  id: string
  title: string
  description: string | null
  is_mandatory: boolean
  is_completed: boolean
}

export type SurveyOption = {
  id: string
  text: string
  order: number
}

export type SurveyQuestion = {
  id: string
  text: string
  question_type: "single" | "multi" | "text"
  is_required: boolean
  order: number
  options: SurveyOption[]
}

export type SurveyDetail = {
  id: string
  title: string
  description: string | null
  is_mandatory: boolean
  questions: SurveyQuestion[]
}

export type SubmitAnswer = {
  question_id: string
  option_id?: string | null
  free_text?: string | null
}

export type SubmitResponse = {
  response_id: string
  is_validated: boolean
  validation_result: string | null
}

export async function getSurveys(): Promise<SurveyListItem[]> {
  const { data } = await baseClient.get<SurveyListItem[]>("/api/surveys")
  return data
}

export async function getPendingMandatory(): Promise<SurveyListItem[]> {
  const { data } = await baseClient.get<SurveyListItem[]>("/api/surveys/mandatory/pending")
  return data
}

export async function getSurvey(id: string): Promise<SurveyDetail> {
  const { data } = await baseClient.get<SurveyDetail>(`/api/surveys/${id}`)
  return data
}

export async function submitSurvey(id: string, answers: SubmitAnswer[]): Promise<SubmitResponse> {
  const { data } = await baseClient.post<SubmitResponse>(`/api/surveys/${id}/submit`, { answers })
  return data
}

export async function getMyAnswers(id: string): Promise<SubmitAnswer[]> {
  const { data } = await baseClient.get<SubmitAnswer[]>(`/api/surveys/${id}/my-answers`)
  return data
}

// Admin API
export type SurveyCreatePayload = {
  title: string
  description?: string
  is_mandatory?: boolean
  questions: {
    text: string
    question_type?: string
    order?: number
    options: { text: string; order?: number }[]
  }[]
}

export async function createSurveyAdmin(payload: SurveyCreatePayload): Promise<SurveyDetail> {
  const { data } = await baseClient.post<SurveyDetail>("/api/admin/surveys", payload)
  return data
}

export async function updateSurveyAdmin(id: string, payload: Partial<SurveyCreatePayload> & { is_active?: boolean }): Promise<SurveyDetail> {
  const { data } = await baseClient.put<SurveyDetail>(`/api/admin/surveys/${id}`, payload)
  return data
}

export async function deleteSurveyAdmin(id: string): Promise<void> {
  await baseClient.delete(`/api/admin/surveys/${id}`)
}
