import { useEffect, useState } from "react"
import { useUser } from "~/modules/user/lib/use-user"
import {
  getArticles, getArticle, getCategories, createArticleAdmin, updateArticleAdmin, deleteArticleAdmin, createCategoryAdmin,
  type ArticleListItem, type Category,
} from "~/modules/articles/api/articles"

export default function AdminArticles() {
  const { user } = useUser()
  const [articles, setArticles] = useState<ArticleListItem[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [showCatForm, setShowCatForm] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)

  const [title, setTitle] = useState("")
  const [slug, setSlug] = useState("")
  const [contentMd, setContentMd] = useState("")
  const [categoryId, setCategoryId] = useState("")
  const [specialization, setSpecialization] = useState("")
  const [catName, setCatName] = useState("")
  const [catSlug, setCatSlug] = useState("")

  const load = async () => {
    try {
      const [a, c] = await Promise.all([getArticles(), getCategories()])
      setArticles(a); setCategories(c)
    } catch {} finally { setLoading(false) }
  }

  useEffect(() => { if (user.isAuthorized) load() }, [user.isAuthorized])

  if (!user.isAuthorized) return <div className="flex h-full items-center justify-center"><p className="text-sm text-[#C5CBD3]">Авторизуйтесь</p></div>

  const handleSaveArticle = async () => {
    if (!title.trim() || !slug.trim() || !contentMd.trim()) { setError("Заполните обязательные поля"); return }
    setSaving(true); setError(null)
    try {
      const payload = {
        title, slug,
        content_md: contentMd,
        category_id: categoryId || undefined,
        specialization: specialization || undefined,
      }
      if (editingId) {
        await updateArticleAdmin(editingId, payload)
      } else {
        await createArticleAdmin(payload)
      }
      setShowForm(false); setEditingId(null); setTitle(""); setSlug(""); setContentMd(""); setCategoryId(""); setSpecialization("")
      await load()
    } catch (err: any) {
      setError(err.response?.data?.detail || "Ошибка")
    } finally { setSaving(false) }
  }

  const handleEditArticle = async (articleSlug: string) => {
    try {
      const article = await getArticle(articleSlug)
      setTitle(article.title)
      setSlug(article.slug)
      setContentMd(article.content_md)
      setCategoryId(article.category?.id || "")
      setSpecialization(article.specialization || "")
      setEditingId(article.id)
      setShowForm(true)
      setError(null)
    } catch (err: any) {
      setError(err.response?.data?.detail || "Не удалось загрузить статью")
    }
  }

  const handleSaveCategory = async () => {
    if (!catName.trim() || !catSlug.trim()) { setError("Заполните поля категории"); return }
    try {
      await createCategoryAdmin({ name: catName, slug: catSlug })
      setCatName(""); setCatSlug(""); setShowCatForm(false)
      await load()
    } catch (err: any) { setError(err.response?.data?.detail || "Ошибка") }
  }

  const handleDelete = async (id: string) => {
    try { await deleteArticleAdmin(id); setArticles((p) => p.filter((a) => a.id !== id)) }
    catch (err: any) { setError(err.response?.data?.detail || "Ошибка") }
  }

  const inputCls = "w-full rounded-lg border border-[#C5CBD3] px-3 py-2 text-sm outline-none focus:border-[#3649F9] dark:border-gray-600 dark:bg-[#1e293b] dark:text-gray-200 dark:placeholder-gray-500"

  if (loading) return <div className="flex h-full items-center justify-center"><p className="text-sm text-[#C5CBD3]">Загрузка...</p></div>

  if (showForm) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-6 md:p-8">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-xl font-bold text-gray-900 md:text-2xl dark:text-gray-100">{editingId ? "Редактирование статьи" : "Новая статья"}</h1>
          <button onClick={() => { setShowForm(false); setEditingId(null) }} className="text-sm text-[#C5CBD3]">Отмена</button>
        </div>
        <div className="space-y-4">
          <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Заголовок" className={inputCls} />
          <input value={slug} onChange={(e) => setSlug(e.target.value)} placeholder="URL slug (латиница)" className={inputCls} />
          <select value={categoryId} onChange={(e) => setCategoryId(e.target.value)} className={inputCls}>
            <option value="">Без категории</option>
            {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
          <input value={specialization} onChange={(e) => setSpecialization(e.target.value)} placeholder="Специализация (frontend, backend, ...)" className={inputCls} />
          <textarea value={contentMd} onChange={(e) => setContentMd(e.target.value)} placeholder="Содержимое (Markdown)" className={inputCls + " min-h-[150px] font-mono text-xs md:min-h-[300px]"} />
          {error && <p className="text-sm text-red-500">{error}</p>}
          <button onClick={handleSaveArticle} disabled={saving}
            className="rounded-lg bg-[#3649F9] px-8 py-3 text-sm font-medium text-white hover:bg-[#3649F9]/90 disabled:opacity-50">
            {saving ? "Сохранение..." : editingId ? "Сохранить изменения" : "Опубликовать"}
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-6 md:p-8">
      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between md:mb-8">
        <h1 className="text-xl font-bold text-gray-900 md:text-2xl dark:text-gray-100">Управление статьями</h1>
        <div className="flex gap-2">
          <button onClick={() => setShowCatForm(true)} className="rounded-lg border border-[#3649F9] px-4 py-2 text-xs text-[#3649F9]">+ Категория</button>
          <button onClick={() => { setEditingId(null); setTitle(""); setSlug(""); setContentMd(""); setCategoryId(""); setSpecialization(""); setShowForm(true); setError(null) }} className="rounded-lg bg-[#3649F9] px-4 py-2 text-xs text-white">+ Статья</button>
        </div>
      </div>

      {showCatForm && (
        <div className="mb-6 flex flex-col gap-2 rounded-xl border border-gray-100 p-4 sm:flex-row sm:items-end dark:border-gray-700 dark:bg-[#1e293b]">
          <input value={catName} onChange={(e) => setCatName(e.target.value)} placeholder="Название" className={inputCls + " flex-1"} />
          <input value={catSlug} onChange={(e) => setCatSlug(e.target.value)} placeholder="Slug" className={inputCls + " flex-1"} />
          <button onClick={handleSaveCategory} className="rounded-lg bg-[#3649F9] px-4 py-2 text-xs text-white">OK</button>
          <button onClick={() => setShowCatForm(false)} className="text-xs text-[#C5CBD3]">&times;</button>
        </div>
      )}

      {error && <p className="mb-4 text-sm text-red-500">{error}</p>}

      {articles.length === 0 ? (
        <p className="text-sm text-[#C5CBD3]">Статей пока нет</p>
      ) : (
        <div className="space-y-3">
          {articles.map((a) => (
            <div key={a.id} className="flex flex-col gap-2 rounded-xl border border-gray-100 p-4 sm:flex-row sm:items-center sm:justify-between dark:border-gray-700 dark:bg-[#1e293b]">
              <div className="min-w-0">
                <p className="text-sm font-medium text-gray-800 dark:text-gray-200">{a.title}</p>
                <div className="mt-0.5 flex gap-2 text-xs text-[#C5CBD3]">
                  {a.category && <span>{a.category.name}</span>}
                  {a.specialization && <span>{a.specialization}</span>}
                  <span>/{a.slug}</span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button onClick={() => handleEditArticle(a.slug)} className="text-xs text-[#3649F9] hover:underline">Редактировать</button>
                <button onClick={() => handleDelete(a.id)} className="text-xs text-red-400 hover:text-red-500">Удалить</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
