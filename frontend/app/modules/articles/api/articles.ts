import { baseClient } from "~/shared/api/axios-client"

export type Category = {
  id: string
  name: string
  slug: string
  order: number
}

export type ArticleListItem = {
  id: string
  title: string
  slug: string
  specialization: string | null
  category: Category | null
}

export type ArticleDetail = {
  id: string
  title: string
  slug: string
  content_md: string
  specialization: string | null
  category: Category | null
}

export async function getCategories(): Promise<Category[]> {
  const { data } = await baseClient.get<Category[]>("/api/articles/categories")
  return data
}

export async function getArticles(params?: { category?: string; specialization?: string }): Promise<ArticleListItem[]> {
  const { data } = await baseClient.get<ArticleListItem[]>("/api/articles", { params })
  return data
}

export async function getArticle(slug: string): Promise<ArticleDetail> {
  const { data } = await baseClient.get<ArticleDetail>(`/api/articles/${slug}`)
  return data
}

// Admin
export async function createArticleAdmin(payload: {
  title: string; slug: string; content_md: string; category_id?: string; specialization?: string
}): Promise<ArticleDetail> {
  const { data } = await baseClient.post<ArticleDetail>("/api/admin/articles", payload)
  return data
}

export async function updateArticleAdmin(id: string, payload: {
  title: string; slug: string; content_md: string; category_id?: string; specialization?: string
}): Promise<ArticleDetail> {
  const { data } = await baseClient.put<ArticleDetail>(`/api/admin/articles/${id}`, payload)
  return data
}

export async function deleteArticleAdmin(id: string): Promise<void> {
  await baseClient.delete(`/api/admin/articles/${id}`)
}

export async function createCategoryAdmin(payload: { name: string; slug: string; order?: number }): Promise<Category> {
  const { data } = await baseClient.post<Category>("/api/admin/articles/categories", payload)
  return data
}
