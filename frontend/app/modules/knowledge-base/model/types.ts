export type KnowledgeBaseCard = {
  id: string
  informationId: string
  title: string
  description: string
  createdAt: string
  updatedAt: string
}

export type KnowledgeBaseCollection = {
  id: string
  title: string
  createdAt: string
  cards: KnowledgeBaseCard[]
}

export type KnowledgeBaseResponse = {
  items: KnowledgeBaseCollection[]
  total: number
  next?: string | null
  prev?: string | null
}
