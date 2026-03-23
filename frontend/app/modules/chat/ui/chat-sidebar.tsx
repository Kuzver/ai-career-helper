import { useEffect, useRef, useState } from "react"
import { useNavigate, useSearchParams } from "react-router-dom"
import { getChats, renameChat, deleteChat } from "~/modules/chat/api/chats"
import type { Chat } from "~/modules/chat/model/types"

export function ChatSidebar() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const selectedChatId = searchParams.get("chatId")

  const [chats, setChats] = useState<Chat[]>([])
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editTitle, setEditTitle] = useState("")
  const [contextMenu, setContextMenu] = useState<{ id: string; x: number; y: number } | null>(null)
  const editRef = useRef<HTMLInputElement>(null)

  const loadChats = async () => {
    try {
      const data = await getChats({ limit: 50, offset: 0 })
      setChats(data.items)
    } catch {}
  }

  useEffect(() => { loadChats() }, [selectedChatId])

  useEffect(() => {
    const handler = () => loadChats()
    window.addEventListener("chats-updated", handler)
    return () => window.removeEventListener("chats-updated", handler)
  }, [])

  useEffect(() => {
    if (editingId && editRef.current) editRef.current.focus()
  }, [editingId])

  useEffect(() => {
    const close = () => setContextMenu(null)
    window.addEventListener("click", close)
    return () => window.removeEventListener("click", close)
  }, [])

  const handleNewChat = () => {
    navigate("/chat", { replace: true })
  }

  const handleSelect = (chatId: string) => {
    navigate(`/chat?chatId=${chatId}`, { replace: true })
  }

  const handleContextMenu = (e: React.MouseEvent, chatId: string) => {
    e.preventDefault()
    setContextMenu({ id: chatId, x: e.clientX, y: e.clientY })
  }

  const handleStartRename = (chat: Chat) => {
    setEditingId(chat.id)
    setEditTitle(chat.title)
    setContextMenu(null)
  }

  const handleRename = async () => {
    if (!editingId || !editTitle.trim()) { setEditingId(null); return }
    try {
      await renameChat(editingId, editTitle.trim())
      setChats((prev) => prev.map((c) => c.id === editingId ? { ...c, title: editTitle.trim() } : c))
    } catch {}
    setEditingId(null)
  }

  const handleDelete = async (chatId: string) => {
    setContextMenu(null)
    try {
      await deleteChat(chatId)
      setChats((prev) => prev.filter((c) => c.id !== chatId))
      if (selectedChatId === chatId) {
        navigate("/chat", { replace: true })
      }
    } catch {}
  }

  return (
    <div className="flex flex-1 flex-col overflow-hidden border-t border-gray-100 pt-3">
      <div className="flex items-center justify-between px-4 pb-2">
        <span className="text-xs font-medium text-[#6D7C90]">Чаты</span>
        <button onClick={handleNewChat}
          className="rounded px-2 py-0.5 text-xs text-[#3649F9] hover:bg-[#E8EAFF]">
          + Новый
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-2">
        {chats.map((chat) => (
          <div key={chat.id} className="relative">
            {editingId === chat.id ? (
              <input
                ref={editRef}
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                onBlur={handleRename}
                onKeyDown={(e) => {
                  if (e.key === "Enter") handleRename()
                  if (e.key === "Escape") setEditingId(null)
                }}
                className="w-full rounded-md border border-[#3649F9] px-3 py-1.5 text-xs outline-none"
              />
            ) : (
              <button
                onClick={() => handleSelect(chat.id)}
                onContextMenu={(e) => handleContextMenu(e, chat.id)}
                className={[
                  "w-full truncate rounded-md px-3 py-1.5 text-left text-xs transition-colors",
                  chat.id === selectedChatId
                    ? "bg-[#E8EAFF] font-medium text-[#3649F9]"
                    : "text-[#6D7C90] hover:bg-gray-50",
                ].join(" ")}
                title={chat.title}
              >
                {chat.title}
              </button>
            )}
          </div>
        ))}

        {chats.length === 0 && (
          <p className="px-3 py-2 text-xs text-[#C5CBD3]">Нет чатов</p>
        )}
      </div>

      {contextMenu && (
        <div
          className="fixed z-50 rounded-lg border bg-white py-1 shadow-lg"
          style={{ left: contextMenu.x, top: contextMenu.y }}
        >
          <button
            onClick={() => {
              const chat = chats.find((c) => c.id === contextMenu.id)
              if (chat) handleStartRename(chat)
            }}
            className="block w-full px-4 py-1.5 text-left text-xs text-gray-600 hover:bg-gray-50"
          >
            Переименовать
          </button>
          <button
            onClick={() => handleDelete(contextMenu.id)}
            className="block w-full px-4 py-1.5 text-left text-xs text-red-500 hover:bg-red-50"
          >
            Удалить
          </button>
        </div>
      )}
    </div>
  )
}
