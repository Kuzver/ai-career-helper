import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"
import Markdown from "react-markdown"
import remarkGfm from "remark-gfm"
import rehypeSanitize from "rehype-sanitize"
import { getArticle, type ArticleDetail } from "~/modules/articles/api/articles"

export default function ArticlePage() {
  const { slug } = useParams<{ slug: string }>()
  const [article, setArticle] = useState<ArticleDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!slug) return
    getArticle(slug)
      .then(setArticle)
      .catch(() => setError("Статья не найдена"))
      .finally(() => setLoading(false))
  }, [slug])

  if (loading) return <div className="flex h-full items-center justify-center"><p className="text-sm text-[#C5CBD3]">Загрузка...</p></div>
  if (error) return <div className="flex h-full items-center justify-center"><p className="text-sm text-red-500">{error}</p></div>
  if (!article) return null

  return (
    <div className="mx-auto max-w-3xl p-8">
      <Link to="/knowledge-base" className="mb-6 inline-block text-sm text-[#3649F9] hover:underline">
        &larr; Назад к статьям
      </Link>
      {article.category && (
        <span className="mb-3 ml-4 inline-block rounded bg-[#E8EAFF] px-2 py-0.5 text-xs text-[#3649F9]">
          {article.category.name}
        </span>
      )}
      <h1 className="mb-6 text-2xl font-bold text-gray-900">{article.title}</h1>
      <div className="bot-markdown prose max-w-none text-sm leading-relaxed text-gray-700">
        <Markdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeSanitize]}>{article.content_md}</Markdown>
      </div>
    </div>
  )
}
