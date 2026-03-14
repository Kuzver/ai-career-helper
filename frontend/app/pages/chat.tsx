import { useEffect, useMemo } from "react"
import {
  Link,
  useFetcher,
  useLoaderData,
  useNavigation,
  useSearchParams,
} from "react-router"

import type { Route } from "./+types/chat"
import { createChat, getChatById, getChats } from "~/modules/chat/api/chats"
import type { ChatWithMessages } from "~/modules/chat/model/types"
import { Button } from "~/shared/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "~/shared/components/ui/card"
import { Input } from "~/shared/components/ui/input"
import { Skeleton } from "~/shared/components/ui/skeleton"

const CHATS_LIMIT = 50
const MESSAGES_LIMIT = 50

export function meta({}: Route.MetaArgs) {
  return [{ title: "Чаты" }]
}

export async function clientLoader({ request }: Route.ClientLoaderArgs) {
  const url = new URL(request.url)
  const selectedChatId = url.searchParams.get("chatId")
  const chatsData = await getChats({ limit: CHATS_LIMIT, offset: 0 })

  const chats = chatsData.items
  const fallbackChatId = chats[0]?.id ?? null
  const chatId =
    selectedChatId && chats.some((chat) => chat.id === selectedChatId)
      ? selectedChatId
      : fallbackChatId

  let selectedChat: ChatWithMessages | null = null
  if (chatId) {
    const chatData = await getChatById({
      id: chatId,
      limit: MESSAGES_LIMIT,
      offset: 0,
    })
    selectedChat = chatData.items[0] ?? null
  }

  return {
    chats,
    selectedChat,
    selectedChatId: chatId,
  }
}

export async function clientAction({ request }: Route.ActionArgs) {
  const formData = await request.formData()
  const title = String(formData.get("title") ?? "").trim()

  if (!title) {
    return { error: "Введите название чата" }
  }

  const chat = await createChat(title)
  return { chat }
}

export default function Chat() {
  const { chats, selectedChat, selectedChatId } = useLoaderData<typeof clientLoader>()
  const [, setSearchParams] = useSearchParams()
  const fetcher = useFetcher<typeof clientAction>()
  const navigation = useNavigation()
  const isLoading = navigation.state === "loading"

  useEffect(() => {
    if (fetcher.data?.chat) {
      setSearchParams({ chatId: fetcher.data.chat.id })
    }
  }, [fetcher.data, setSearchParams])

  const selectedTitle = useMemo(() => {
    if (!selectedChatId) return "Выберите чат"
    return chats.find((chat) => chat.id === selectedChatId)?.title ?? "Чат"
  }, [chats, selectedChatId])

  return (
    <div className="grid min-h-[calc(100vh-180px)] gap-6 lg:grid-cols-[320px_1fr]">
      <div className="flex flex-col gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Ваши чаты</CardTitle>
            <CardDescription>Выберите диалог или создайте новый.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <fetcher.Form method="post" className="flex gap-2">
              <Input name="title" placeholder="Новый чат" autoComplete="off" />
              <Button type="submit" disabled={fetcher.state === "submitting"}>
                Создать
              </Button>
            </fetcher.Form>
            {fetcher.data?.error && (
              <p className="text-sm text-destructive">{fetcher.data.error}</p>
            )}
            <div className="space-y-2">
              {chats.length === 0 ? (
                <p className="text-sm text-muted-foreground">Чатов пока нет.</p>
              ) : (
                chats.map((chat) => {
                  const isActive = chat.id === selectedChatId
                  return (
                    <Link
                      key={chat.id}
                      to={`?chatId=${chat.id}`}
                      className={[
                        "flex flex-col gap-1 rounded-lg border px-3 py-2 text-sm transition",
                        isActive
                          ? "border-primary/40 bg-primary/10 text-primary"
                          : "hover:bg-muted/60",
                      ].join(" ")}
                    >
                      <span className="font-medium text-foreground">{chat.title}</span>
                      <span className="text-xs text-muted-foreground">
                        Последняя активность: {new Date(chat.lastActivityTime).toLocaleString("ru-RU")}
                      </span>
                    </Link>
                  )
                })
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="flex min-h-[520px] flex-col lg:min-h-full">
        <CardHeader>
          <CardTitle>{selectedTitle}</CardTitle>
          <CardDescription>
            {selectedChat ? "История сообщений чата." : "Выберите чат в списке слева."}
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-1 flex-col gap-4">
          {isLoading ? (
            <div className="flex flex-1 flex-col gap-3 rounded-lg border bg-muted/20 p-4">
              <Skeleton className="h-10 w-2/3" />
              <Skeleton className="h-16 w-full" />
              <Skeleton className="h-16 w-5/6" />
              <Skeleton className="h-16 w-4/6" />
            </div>
          ) : selectedChat ? (
            <div className="flex flex-1 flex-col gap-3 overflow-y-auto rounded-lg border bg-muted/20 p-4">
              {selectedChat.messages.length === 0 ? (
                <p className="text-sm text-muted-foreground">Сообщений пока нет.</p>
              ) : (
                selectedChat.messages.map((message) => (
                  <div key={message.id} className="rounded-lg border bg-background p-3 text-sm">
                    <p className="text-xs font-medium text-muted-foreground">
                      {message.senderTypeId}
                    </p>
                    <p>{message.text}</p>
                  </div>
                ))
              )}
            </div>
          ) : (
            <div className="flex flex-1 items-center justify-center rounded-lg border border-dashed text-sm text-muted-foreground">
              Пока не выбран чат.
            </div>
          )}

          <div className="space-y-2">
            <textarea
              className="min-h-[120px] w-full resize-none rounded-lg border bg-muted/40 px-3 py-2 text-sm text-muted-foreground"
              placeholder="Введите сообщение..."
              disabled
            />
            <Button variant="outline" disabled className="w-full">
              Отправка пока недоступна
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
