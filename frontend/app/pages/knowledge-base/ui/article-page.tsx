import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"
import Markdown from "react-markdown"
import remarkGfm from "remark-gfm"
import rehypeSanitize from "rehype-sanitize"
import { getArticle, type ArticleDetail } from "~/modules/articles/api/articles"
import { baseClient } from "~/shared/api/axios-client"

export default function ArticlePage() {
  const { slug } = useParams<{ slug: string }>()
  const [article, setArticle] = useState<ArticleDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showExport, setShowExport] = useState(false)

  useEffect(() => {
    if (!slug) return
    getArticle(slug)
      .then(setArticle)
      .catch(() => setError("Статья не найдена"))
      .finally(() => setLoading(false))
  }, [slug])

  const handleExport = async (format: "md" | "docx" | "html") => {
    if (!slug) return
    try {
      const { data } = await baseClient.post("/api/export/article", { slug, format }, { responseType: "blob" })
      const url = URL.createObjectURL(data)
      const a = document.createElement("a")
      a.href = url
      a.download = `${slug}.${format}`
      a.click()
      URL.revokeObjectURL(url)
    } catch {}
    setShowExport(false)
  }

  if (loading) return <div className="flex h-full items-center justify-center"><p className="text-sm text-[#C5CBD3]">Загрузка...</p></div>
  if (error) return <div className="flex h-full items-center justify-center"><p className="text-sm text-red-500">{error}</p></div>
  if (!article) return null

  return (
    <div className="mx-auto max-w-3xl p-8">
      <div className="mb-6 flex items-center justify-between">
        <Link to="/knowledge-base" className="text-sm text-[#3649F9] hover:underline">
          &larr; Назад к статьям
        </Link>
        <div className="relative">
          <button onClick={() => setShowExport((v) => !v)}
            className="rounded-lg border border-gray-200 px-3 py-1.5 text-xs text-[#6D7C90] hover:border-[#3649F9] hover:text-[#3649F9] dark:border-gray-700">
            Скачать
          </button>
          {showExport && (
            <div className="absolute right-0 top-full z-10 mt-1 rounded-lg border bg-white py-1 shadow-lg dark:border-gray-700 dark:bg-[#1e293b]">
              {(["md", "docx", "html"] as const).map((fmt) => (
                <button key={fmt} onClick={() => handleExport(fmt)}
                  className="block w-full px-4 py-1.5 text-left text-xs text-gray-600 hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-700">
                  {fmt.toUpperCase()}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
      {article.category && (
        <span className="mb-3 inline-block rounded bg-[#E8EAFF] px-2 py-0.5 text-xs text-[#3649F9] dark:bg-[#3649F9]/20">
          {article.category.name}
        </span>
      )}
      <h1 className="mb-6 text-2xl font-bold text-gray-900 dark:text-gray-100">{article.title}</h1>
      <div className="bot-markdown prose max-w-none text-sm leading-relaxed text-gray-700 dark:text-gray-300">
        <Markdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeSanitize]}>{article.content_md}</Markdown>
      </div>
    </div>
  )
}
