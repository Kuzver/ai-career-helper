import { useEffect, useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { getArticles, getCategories, type ArticleListItem, type Category } from "~/modules/articles/api/articles"
import { useUser } from "~/modules/user/lib/use-user"
import { getProfile } from "~/modules/user/api/profile"
import { GridSkeleton } from "~/shared/components/ui/skeletons"

export default function KnowledgeBase() {
  const { user } = useUser()
  const navigate = useNavigate()
  const [articles, setArticles] = useState<ArticleListItem[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [showAll, setShowAll] = useState(false)
  const [loading, setLoading] = useState(true)
  const [userSpec, setUserSpec] = useState<string | null>(null)

  useEffect(() => {
    if (!user.isAuthorized) { setLoading(false); return }

    const load = async () => {
      try {
        const [cats, profile] = await Promise.all([getCategories(), getProfile()])
        setCategories(cats)
        setUserSpec(profile.specialization || null)

        const params: Record<string, string> = {}
        if (profile.specialization && !showAll) {
          params.specialization = profile.specialization
        }
        const items = await getArticles(params)
        setArticles(items)
      } catch {}
      setLoading(false)
    }
    load()
  }, [user.isAuthorized, showAll])

  if (!user.isAuthorized) {
    return (
      <div className="flex h-full flex-col items-center justify-center">
        <p className="mb-2 text-lg font-medium text-gray-600">База знаний</p>
        <p className="mb-6 text-sm text-[#C5CBD3]">Войдите, чтобы читать статьи</p>
        <Link to="/sign-in" className="rounded-lg bg-[#3649F9] px-6 py-2.5 text-sm font-medium text-white">Войти</Link>
      </div>
    )
  }

  if (loading) return <div className="p-8"><GridSkeleton /></div>

  const filtered = selectedCategory
    ? articles.filter((a) => a.category?.slug === selectedCategory)
    : articles

  return (
    <div className="p-8">
      <div className="mb-8 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">База знаний</h1>
        <div className="flex items-center gap-3">
          {userSpec && (
            <button
              onClick={() => setShowAll((v) => !v)}
              className="rounded-lg border border-gray-200 px-3 py-1.5 text-xs text-[#6D7C90] hover:border-[#3649F9] hover:text-[#3649F9] dark:border-gray-700"
            >
              {showAll ? "По моей специализации" : "Показать все"}
            </button>
          )}
        </div>
      </div>

      {/* Категории */}
      {categories.length > 0 && (
        <div className="mb-6 flex flex-wrap gap-2">
          <button
            onClick={() => setSelectedCategory(null)}
            className={["rounded-full px-4 py-1.5 text-xs font-medium transition-colors",
              !selectedCategory ? "bg-[#3649F9] text-white" : "bg-gray-100 text-[#6D7C90] hover:bg-[#E8EAFF]",
            ].join(" ")}
          >
            Все
          </button>
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.slug === selectedCategory ? null : cat.slug)}
              className={["rounded-full px-4 py-1.5 text-xs font-medium transition-colors",
                selectedCategory === cat.slug ? "bg-[#3649F9] text-white" : "bg-gray-100 text-[#6D7C90] hover:bg-[#E8EAFF] dark:bg-gray-700",
              ].join(" ")}
            >
              {cat.name}
            </button>
          ))}
        </div>
      )}

      {filtered.length === 0 ? (
        <p className="text-sm text-[#C5CBD3]">Статей пока нет</p>
      ) : (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filtered.map((article) => (
            <button
              key={article.id}
              onClick={() => navigate(`/knowledge-base/${article.slug}`)}
              className="rounded-2xl border border-gray-200 bg-white p-6 text-left transition-shadow hover:shadow-md dark:border-gray-700 dark:bg-[#1e293b]"
            >
              {article.category && (
                <span className="mb-2 inline-block rounded bg-[#E8EAFF] px-2 py-0.5 text-xs text-[#3649F9]">
                  {article.category.name}
                </span>
              )}
              <h3 className="mb-2 text-base font-semibold text-gray-900 dark:text-gray-100">{article.title}</h3>
              {article.specialization && (
                <p className="text-xs text-[#C5CBD3]">{article.specialization}</p>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
