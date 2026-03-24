import { useEffect, useRef, useState } from "react"
import type { LoaderFunctionArgs } from "react-router-dom"
import { useLoaderData, useNavigate, useRevalidator, useSearchParams } from "react-router-dom"
import Markdown from "react-markdown"
import remarkGfm from "remark-gfm"
import rehypeSanitize from "rehype-sanitize"
import { createChat, getChatById, getChats, sendMessage, exportMessage } from "~/modules/chat/api/chats"
import { useUser } from "~/modules/user/lib/use-user"
import { Logo } from "~/shared/components/ui/logo"
import type { Chat, ChatWithMessages, Message } from "~/modules/chat/model/types"

function cleanLegacyContext(text: string): string {
  return text.replace(/^\[Контекст пользователя:[^\]]*\]\n?/i, "")
}

const CHATS_LIMIT = 50
const MESSAGES_LIMIT = 100

export async function loader({ request }: LoaderFunctionArgs) {
  try {
    const url = new URL(request.url)
    const chatId = url.searchParams.get("chatId")

    const chatsData = await getChats({ limit: CHATS_LIMIT, offset: 0 })
    const chats = chatsData.items

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
  return <div className="bot-markdown"><Markdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeSanitize]}>{text}</Markdown></div>
}

export default function ChatPage() {
  const data = useLoaderData<typeof loader>()
  const revalidator = useRevalidator()
  const [, setSearchParams] = useSearchParams()
  const navigate = useNavigate()
  const { user } = useUser()

  const [messageText, setMessageText] = useState("")
  const [isSending, setIsSending] = useState(false)
  const [optimisticText, setOptimisticText] = useState<string | null>(null)
  const [sendError, setSendError] = useState<string | null>(null)
  const [attachedFile, setAttachedFile] = useState<File | null>(null)
  const [dragOver, setDragOver] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const selectedChatId = data.selectedChatId
  const serverMessages = data.selectedChat?.messages ?? []

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [serverMessages.length, isSending, optimisticText])

  useEffect(() => {
    if (optimisticText && serverMessages.some((m) => m.senderTypeId === "user" && (m.text === optimisticText || cleanLegacyContext(m.text) === optimisticText || m.text.includes(optimisticText)))) {
      setOptimisticText(null)
    }
  }, [serverMessages, optimisticText])

  if (!user.isAuthorized) {
    return (
      <div className="flex h-full flex-col items-center justify-center">
        <Logo size={64} />
        <p className="mb-2 text-lg font-medium text-gray-600">Войдите в аккаунт</p>
        <p className="mb-6 text-sm text-[#C5CBD3]">Чтобы начать общение с ИИ-помощником</p>
        <button onClick={() => navigate("/sign-in")}
          className="rounded-lg bg-[#3649F9] px-6 py-2.5 text-sm font-medium text-white hover:bg-[#3649F9]/90">
          Войти
        </button>
      </div>
    )
  }

  const handleSendMessage = async () => {
    const text = messageText.trim()
    if ((!text && !attachedFile) || isSending) return

    setIsSending(true)
    setSendError(null)
    setMessageText("")
    setOptimisticText(text || (attachedFile ? `[${attachedFile.name}]` : ""))

    try {
      let chatId = selectedChatId

      if (!chatId) {
        const title = text.length > 50 ? text.slice(0, 50) + "..." : (text || "Новый чат")
        const newChat = await createChat(title)
        chatId = newChat.id
        setSearchParams({ chatId }, { replace: true })
      }

      await sendMessage(chatId, text || "Проанализируй файл", attachedFile || undefined)
      setOptimisticText(null)
      setAttachedFile(null)
      revalidator.revalidate()
      window.dispatchEvent(new Event("chats-updated"))
    } catch (err) {
      console.error("Send error:", err)
      setSendError("Не удалось отправить. Попробуйте ещё раз.")
      setOptimisticText(null)
    } finally {
      setIsSending(false)
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) setAttachedFile(file)
    e.target.value = ""
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) {
      const ext = file.name.split(".").pop()?.toLowerCase()
      if (["pdf", "docx", "md"].includes(ext || "")) {
        setAttachedFile(file)
      } else {
        setSendError("Допустимые форматы: PDF, DOCX, MD")
      }
    }
  }

  const handleExport = async (messageId: string, format: "md" | "docx" | "html") => {
    try {
      const blob = await exportMessage(messageId, format)
      const url = URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `response.${format}`
      a.click()
      URL.revokeObjectURL(url)
    } catch {
      setSendError("Не удалось экспортировать")
    }
  }

  const showOptimistic = optimisticText && !serverMessages.some(
    (m) => m.senderTypeId === "user" && (m.text === optimisticText || cleanLegacyContext(m.text) === optimisticText || m.text.includes(optimisticText))
  )

  return (
    <div
      className={["flex h-full flex-col", dragOver ? "ring-2 ring-inset ring-[#3649F9]/30" : ""].join(" ")}
      onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
      onDragLeave={() => setDragOver(false)}
      onDrop={handleDrop}
    >
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-8 py-6 dark:bg-[#0f172a]">
        {serverMessages.length === 0 && !showOptimistic && !isSending ? (
          <div className="flex h-full flex-col items-center justify-center">
            <Logo size={64} />
            <p className="mb-2 text-lg font-medium text-gray-600 dark:text-gray-300">ИИ-помощник</p>
            <p className="mb-6 text-sm text-[#C5CBD3]">Выберите тему или напишите свой вопрос</p>
            <div className="grid w-full max-w-xl grid-cols-2 gap-3 px-4">
              {[
                { icon: "📝", text: "Помоги составить резюме", desc: "ATS-оптимизация" },
                { icon: "🗺️", text: "Составь мне roadmap", desc: "План обучения" },
                { icon: "🎯", text: "Подготовь к собеседованию", desc: "Вопросы и кейсы" },
                { icon: "📚", text: "Что изучить для frontend", desc: "Курсы и ресурсы" },
                { icon: "💼", text: "Как найти первую работу в IT", desc: "Советы по поиску" },
                { icon: "📊", text: "Проанализируй мои навыки", desc: "Оценка и план" },
              ].map((item) => (
                <button
                  key={item.text}
                  onClick={() => { setMessageText(item.text); }}
                  className="group flex items-start gap-3 rounded-xl border border-gray-100 bg-white p-3.5 text-left transition-all hover:border-[#3649F9]/30 hover:shadow-sm dark:border-gray-700 dark:bg-[#1e293b] dark:hover:border-[#3649F9]/50"
                >
                  <span className="text-xl">{item.icon}</span>
                  <div>
                    <p className="text-sm font-medium text-gray-800 group-hover:text-[#3649F9] dark:text-gray-200">{item.text}</p>
                    <p className="text-xs text-[#C5CBD3]">{item.desc}</p>
                  </div>
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {serverMessages.map((msg) => (
              <MessageBubble key={msg.id} msg={msg} onExport={handleExport} />
            ))}
            {showOptimistic && (
              <div className="flex justify-end gap-3">
                <div className="max-w-lg rounded-2xl bg-[#E8EAFF] px-5 py-3">
                  <p className="text-sm leading-relaxed text-gray-800">{optimisticText}</p>
                </div>
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[#3649F9]">
                  <img src="/icons/icon profile.svg" alt="" className="h-4 w-4 brightness-0 invert" />
                </div>
              </div>
            )}
            {isSending && (
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Logo size={32} />
                  <span className="text-sm font-semibold text-gray-800">ИИ-помощник</span>
                </div>
                <div className="ml-10 rounded-2xl bg-[#E8EAFF] px-5 py-3">
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <span className="inline-block h-2 w-2 animate-pulse rounded-full bg-[#3649F9]" />
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

      {/* Attached file preview */}
      {attachedFile && (
        <div className="flex items-center gap-2 px-8 pb-2">
          <div className="flex items-center gap-2 rounded-lg bg-[#E8EAFF] px-3 py-1.5 text-xs text-[#3649F9]">
            <span>{attachedFile.name}</span>
            <button onClick={() => setAttachedFile(null)} className="ml-1 text-gray-400 hover:text-red-500">&times;</button>
          </div>
        </div>
      )}

      {/* Input */}
      <div className="px-8 pb-6 pt-2">
        <div className="rounded-2xl border border-[#C5CBD3]/50 px-4 pb-3 pt-4 dark:border-gray-700 dark:bg-[#1e293b]">
          <textarea
            placeholder="Спросите про карьеру, резюме, обучение..."
            className="min-h-[80px] w-full resize-none bg-transparent text-sm text-gray-700 placeholder-[#C5CBD3] outline-none dark:text-gray-200"
            value={messageText}
            onChange={(e) => setMessageText(e.target.value)}
            disabled={isSending}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSendMessage() }
            }}
          />
          <div className="flex items-center justify-between pt-1">
            <div className="flex items-center gap-1">
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,.md"
                onChange={handleFileSelect}
                className="hidden"
              />
              <button
                onClick={() => fileInputRef.current?.click()}
                className="rounded-full p-1.5 hover:bg-gray-100"
                title="Прикрепить файл (PDF, DOCX, MD)"
                aria-label="Прикрепить файл"
              >
                <img src="/icons/upload.svg" alt="" className="h-5 w-5 opacity-40" />
              </button>
            </div>
            <button onClick={handleSendMessage}
              disabled={(!messageText.trim() && !attachedFile) || isSending}
              aria-label="Отправить сообщение"
              className="flex h-9 w-9 items-center justify-center rounded-full bg-[#3649F9] text-white hover:bg-[#3649F9]/90 disabled:opacity-40">
              <img src="/icons/write.svg" alt="" className="h-4 w-4 brightness-0 invert" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

function MessageBubble({ msg, onExport }: { msg: Message; onExport: (id: string, fmt: "md" | "docx" | "html") => void }) {
  const [showExport, setShowExport] = useState(false)

  if (msg.senderTypeId === "user") {
    return (
      <div className="flex justify-end gap-3">
        <div className="max-w-lg rounded-2xl bg-[#E8EAFF] px-5 py-3">
          <p className="text-sm leading-relaxed text-gray-800">{cleanLegacyContext(msg.text)}</p>
        </div>
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[#3649F9]">
          <img src="/icons/icon profile.svg" alt="" className="h-4 w-4 brightness-0 invert" />
        </div>
      </div>
    )
  }

  return (
    <div className="group space-y-2">
      <div className="flex items-center gap-2">
        <Logo size={32} />
        <span className="text-sm font-semibold text-gray-800 dark:text-gray-200">ИИ-помощник</span>
      </div>
      <div className="ml-10 max-w-2xl rounded-2xl bg-[#E8EAFF] px-5 py-3 text-sm leading-relaxed text-gray-800 dark:bg-[#3649F9]/15 dark:text-gray-200">
        <BotMessage text={msg.text} />
      </div>
      <div className="relative ml-10">
        <button
          onClick={() => setShowExport((v) => !v)}
          className="rounded px-2 py-0.5 text-xs text-[#C5CBD3] opacity-0 transition-opacity hover:text-[#3649F9] group-hover:opacity-100"
        >
          Скачать
        </button>
        {showExport && (
          <div className="absolute bottom-full left-0 z-10 mb-1 rounded-lg border bg-white py-1 shadow-lg dark:border-gray-700 dark:bg-[#1e293b]">
            {(["md", "docx", "html"] as const).map((fmt) => (
              <button
                key={fmt}
                onClick={() => { onExport(msg.id, fmt); setShowExport(false) }}
                className="block w-full px-4 py-1.5 text-left text-xs text-gray-600 hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-700"
              >
                {fmt.toUpperCase()}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
