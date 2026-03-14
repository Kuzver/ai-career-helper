export type Chat = {
  id: string
  userId: string
  title: string
  startTime: string
  lastActivityTime: string
  createdAt: string
  updatedAt: string
}

export type Message = {
  id: string
  chatId: string
  text: string
  senderTypeId: string
  createdAt: string
  updatedAt: string
}

export type ChatWithMessages = {
  id: string
  title: string
  createdAt: string
  messages: Message[]
}

export type PaginatedResponse<T> = {
  items: T[]
  lenItems: number
  leftLimit: number | null
  leftOffset: number | null
  rightLimit: number | null
  rightOffset: number | null
}
