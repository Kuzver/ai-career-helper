import { baseClient } from "~/shared/api/axios-client"
import type { KnowledgeBaseCollection, KnowledgeBaseResponse } from "../model/types"

type RawCard = {
  id: string
  information_id: string
  title: string
  description: string
  created_at: string
  updated_at: string
}

type RawCollection = {
  id: string
  title: string
  created_at: string
  cards: RawCard[]
}

type RawResponse = {
  items: RawCollection[]
  total: number
  next?: string | null
  prev?: string | null
}

export type GetCardsParams = {
  limit: number
  offset: number
}

const mapCollection = (collection: RawCollection): KnowledgeBaseCollection => ({
  id: collection.id,
  title: collection.title,
  createdAt: collection.created_at,
  cards: collection.cards.map((card) => ({
    id: card.id,
    informationId: card.information_id,
    title: card.title,
    description: card.description,
    createdAt: card.created_at,
    updatedAt: card.updated_at,
  })),
})

const mapResponse = (response: RawResponse): KnowledgeBaseResponse => ({
  items: response.items.map(mapCollection),
  total: response.total,
  next: response.next,
  prev: response.prev,
})

export async function getKnowledgeBaseCards(params: GetCardsParams) {
  const { data } = await baseClient.get<RawResponse>("/api/cards", {
    params,
  })

  return mapResponse(data)
}
