import { useEffect, useRef, useState } from "react"
import type { LoaderFunctionArgs } from "react-router-dom"
import { useLoaderData, useNavigate, useRevalidator, useSearchParams } from "react-router-dom"
import Markdown from "react-markdown"
import { createChat, getChatById, getChats, sendMessage } from "~/modules/chat/api/chats"
import { useUser } from "~/modules/user/lib/use-user"
import type { Chat, ChatWithMessages, Message } from "~/modules/chat/model/types"

const CHATS_LIMIT = 50
const MESSAGES_LIMIT = 100

export async function loader({ request }: LoaderFunctionArgs) {
  try {
    const url = new URL(request.url)
    const chatId = url.searchParams.get("chatId")

    const chatsData = await getChats({ limit: CHATS_LIMIT, offset: 0 })
    const chats = chatsData.items

    // Only load chat if explicitly requested via URL
    let selectedChat: ChatWithMessages | null = null
    if (chatId) {
      try {
        const chatData = await getChatById({ id: chatId, limit: MESSAGES_LIMIT, offset: 0 })
        selectedChat = chatData.items[0] ?? null
      } catch (e) { console.error(e) }
    }

    return { chats, selectedChat, selectedChatId: chatId }
  } catch {
    return { chats: [] as Chat[], selectedChat: null, selectedChatId: null }
  }
}

function BotMessage({ text }: { text: string }) {
  return <div className="bot-markdown"><Markdown>{text}</Markdown></div>
}

function cleanUserText(text: string): string {
  return text.replace(/^\[Контекст пользователя:[^\]]*\]\n?/i, "")
}

export default function ChatPage() {
  const data = useLoaderData<typeof loader>()
  const revalidator = useRevalidator()
  const [, setSearchParams] = useSearchParams()
  const navigate = useNavigate()
  const { user, getProfileContext } = useUser()

  const [messageText, setMessageText] = useState("")
  const [isSending, setIsSending] = useState(false)
  const [optimisticText, setOptimisticText] = useState<string | null>(null)
  const [sendError, setSendError] = useState<string | null>(null)
  const [showChatList, setShowChatList] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const chats = data.chats
  const selectedChatId = data.selectedChatId
  const serverMessages = data.selectedChat?.messages ?? []

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [serverMessages.length, isSending])

  // Clear optimistic text when server catches up
  useEffect(() => {
    if (optimisticText && serverMessages.some((m) => m.senderTypeId === "user" && cleanUserText(m.text) === optimisticText)) {
      setOptimisticText(null)
    }
  }, [serverMessages, optimisticText])

  if (!user.isAuthorized) {
    return (
      <div className="flex h-full flex-col items-center justify-center">
        <div className="mb-6 h-16 w-16 rounded-full bg-[#0157FF]" />
        <p className="mb-2 text-lg font-medium text-gray-600">Войдите в аккаунт</p>
        <p className="mb-6 text-sm text-[#C5CBD3]">Чтобы начать общение с ИИ-помощником</p>
        <button onClick={() => navigate("/sign-in")}
          className="rounded-lg bg-[#0157FF] px-6 py-2.5 text-sm font-medium text-white hover:bg-[#0157FF]/90">
          Войти
        </button>
      </div>
    )
  }

  const handleSendMessage = async () => {
    const text = messageText.trim()
    if (!text || isSending) return

    setIsSending(true)
    setSendError(null)
    setMessageText("")
    setOptimisticText(text)

    const profileCtx = getProfileContext()
    const enrichedText = profileCtx ? `[Контекст пользователя: ${profileCtx}]\n${text}` : text

    try {
      let chatId = selectedChatId

      if (!chatId) {
        const title = text.length > 50 ? text.slice(0, 50) + "..." : text
        const newChat = await createChat(title)
        chatId = newChat.id
        setSearchParams({ chatId }, { replace: true })
      }

      await sendMessage(chatId, enrichedText)
      setOptimisticText(null)
      revalidator.revalidate()
    } catch (err) {
      console.error("Send error:", err)
      setSendError("Не удалось отправить. Попробуйте ещё раз.")
      setOptimisticText(null)
    } finally {
      setIsSending(false)
    }
  }

  const handleNewChat = () => {
    setShowChatList(false)
    setOptimisticText(null)
    setSendError(null)
    // Navigate without chatId — loader won't auto-select any chat
    navigate("/", { replace: true })
  }

  const handleSelectChat = (chatId: string) => {
    setShowChatList(false)
    setOptimisticText(null)
    setSearchParams({ chatId }, { replace: true })
  }

  // Show optimistic user message if server hasn't returned it yet
  const showOptimistic = optimisticText && !serverMessages.some(
    (m) => m.senderTypeId === "user" && cleanUserText(m.text) === optimisticText
  )

  return (
    <div className="flex h-full flex-col">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-8 py-6">
        {serverMessages.length === 0 && !showOptimistic && !isSending ? (
          <div className="flex h-full flex-col items-center justify-center">
            <div className="mb-6 h-16 w-16 rounded-full bg-[#0157FF]" />
            <p className="mb-2 text-lg font-medium text-gray-600">ИИ-помощник</p>
            <p className="text-sm text-[#C5CBD3]">Напишите сообщение, чтобы начать диалог</p>
          </div>
        ) : (
          <div className="space-y-6">
            {serverMessages.map((msg) => (
              <MessageBubble key={msg.id} msg={msg} />
            ))}
            {showOptimistic && (
              <div className="flex justify-end gap-3">
                <div className="max-w-lg rounded-2xl bg-[#E8F0FF] px-5 py-3">
                  <p className="text-sm leading-relaxed text-gray-800">{optimisticText}</p>
                </div>
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[#0157FF]">
                  <img src="/icons/icon profile.svg" alt="" className="h-4 w-4 brightness-0 invert" />
                </div>
              </div>
            )}
            {isSending && (
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <div className="h-8 w-8 shrink-0 rounded-full bg-[#0157FF]" />
                  <span className="text-sm font-semibold text-gray-800">ИИ-помощник</span>
                </div>
                <div className="ml-10 rounded-2xl bg-[#E8F0FF] px-5 py-3">
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <span className="inline-block h-2 w-2 animate-pulse rounded-full bg-[#0157FF]" />
                    Думаю...
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {sendError && <div className="px-8 pb-2"><p className="text-sm text-red-500">{sendError}</p></div>}

      {/* Chat controls */}
      <div className="flex items-center gap-2 border-t border-gray-100 px-8 py-2">
        {selectedChatId && data.selectedChat ? (
          <div className="relative">
            <button onClick={() => setShowChatList((v) => !v)}
              className="max-w-[200px] truncate text-xs text-[#C5CBD3] hover:text-gray-600">
              {data.selectedChat.title} ▾
            </button>
            {showChatList && chats.length > 0 && (
              <div className="absolute bottom-full left-0 z-10 mb-1 max-h-60 w-72 overflow-y-auto rounded-lg border bg-white py-1 shadow-lg">
                {chats.map((chat) => (
                  <button key={chat.id} onClick={() => handleSelectChat(chat.id)}
                    className={["block w-full truncate px-3 py-2 text-left text-sm",
                      chat.id === selectedChatId ? "bg-[#E8F0FF] text-[#0157FF]" : "text-gray-600 hover:bg-gray-50",
                    ].join(" ")}>
                    {chat.title}
                  </button>
                ))}
              </div>
            )}
          </div>
        ) : (
          <span className="text-xs text-[#C5CBD3]">Новый диалог</span>
        )}
        <button onClick={handleNewChat}
          className="ml-auto rounded-md px-3 py-1 text-xs text-[#0157FF] hover:bg-[#E8F0FF]">
          + Новый чат
        </button>
      </div>

      {/* Input */}
      <div className="px-8 pb-6 pt-2">
        <div className="rounded-2xl border border-[#C5CBD3]/50 px-4 pb-3 pt-4">
          <textarea
            placeholder="Спроси меня о чём угодно..."
            className="min-h-[80px] w-full resize-none text-sm text-gray-700 placeholder-[#C5CBD3] outline-none"
            value={messageText}
            onChange={(e) => setMessageText(e.target.value)}
            disabled={isSending}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSendMessage() }
            }}
          />
          <div className="flex items-center justify-between pt-1">
            <button className="rounded-full p-1.5 hover:bg-gray-100">
              <img src="/icons/upload.svg" alt="" className="h-5 w-5 opacity-40" />
            </button>
            <button onClick={handleSendMessage}
              disabled={!messageText.trim() || isSending}
              className="flex h-9 w-9 items-center justify-center rounded-full bg-[#0157FF] text-white hover:bg-[#0157FF]/90 disabled:opacity-40">
              <img src="/icons/write.svg" alt="" className="h-4 w-4 brightness-0 invert" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

function MessageBubble({ msg }: { msg: Message }) {
  if (msg.senderTypeId === "user") {
    return (
      <div className="flex justify-end gap-3">
        <div className="max-w-lg rounded-2xl bg-[#E8F0FF] px-5 py-3">
          <p className="text-sm leading-relaxed text-gray-800">{cleanUserText(msg.text)}</p>
        </div>
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[#0157FF]">
          <img src="/icons/icon profile.svg" alt="" className="h-4 w-4 brightness-0 invert" />
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <div className="h-8 w-8 shrink-0 rounded-full bg-[#0157FF]" />
        <span className="text-sm font-semibold text-gray-800">ИИ-помощник</span>
      </div>
      <div className="ml-10 max-w-2xl rounded-2xl bg-[#E8F0FF] px-5 py-3 text-sm leading-relaxed text-gray-800">
        <BotMessage text={msg.text} />
      </div>
    </div>
  )
}
