import { baseClient } from "~/shared/api/axios-client"
import type { Chat, ChatWithMessages, Message, PaginatedResponse } from "../model/types"

const USER_ID = "21dc573d-663b-419e-a1b6-c48e02b97c67"

type RawChat = {
  id: string
  user_id: string
  title: string
  start_time: string
  last_activity_time: string
  created_at: string
  updated_at: string
}

type RawMessage = {
  id: string
  chat_id: string
  text: string
  sender_type_id: string
  created_at: string
  updated_at: string
}

type RawChatWithMessages = {
  id: string
  title: string
  created_at: string
  messages: RawMessage[]
}

type RawPagination<T> = {
  items: T[] | T
  lenItems: number
  leftLimit: number | null
  leftOffset: number | null
  rightLimit: number | null
  rightOffset: number | null
}

const normalizeItems = <T>(items: T[] | T): T[] => {
  if (Array.isArray(items)) return items
  return [items]
}

const mapChat = (chat: RawChat): Chat => ({
  id: chat.id,
  userId: chat.user_id,
  title: chat.title,
  startTime: chat.start_time,
  lastActivityTime: chat.last_activity_time,
  createdAt: chat.created_at,
  updatedAt: chat.updated_at,
})

const mapMessage = (message: RawMessage): Message => ({
  id: message.id,
  chatId: message.chat_id,
  text: message.text,
  senderTypeId: message.sender_type_id,
  createdAt: message.created_at,
  updatedAt: message.updated_at,
})

const mapChatWithMessages = (chat: RawChatWithMessages): ChatWithMessages => ({
  id: chat.id,
  title: chat.title,
  createdAt: chat.created_at,
  messages: chat.messages.map(mapMessage),
})

export async function getChats(params: { limit: number; offset: number }) {
  const { data } = await baseClient.get<RawPagination<RawChat>>("/api/chats/all", {
    params,
  })

  const items = normalizeItems(data.items).map(mapChat)

  return {
    items,
    lenItems: data.lenItems,
    leftLimit: data.leftLimit,
    leftOffset: data.leftOffset,
    rightLimit: data.rightLimit,
    rightOffset: data.rightOffset,
  } satisfies PaginatedResponse<Chat>
}

export async function createChat(title: string) {
  const { data } = await baseClient.post<RawChatWithMessages>("/api/chats", {
    user_id: USER_ID,
    title,
  })

  return mapChatWithMessages(data)
}

export async function getChatById(params: { id: string; limit: number; offset: number }) {
  const { id, ...rest } = params
  const { data } = await baseClient.get<RawPagination<RawChatWithMessages>>(
    `/api/chats/${id}`,
    { params: rest },
  )

  const items = normalizeItems(data.items).map(mapChatWithMessages)

  return {
    items,
    lenItems: data.lenItems,
    leftLimit: data.leftLimit,
    leftOffset: data.leftOffset,
    rightLimit: data.rightLimit,
    rightOffset: data.rightOffset,
  } satisfies PaginatedResponse<ChatWithMessages>
}
