import { useEffect, useState } from "react"
import { useUser } from "~/modules/user/lib/use-user"
import {
  getSurveys, getSurvey, createSurveyAdmin, updateSurveyAdmin, deleteSurveyAdmin,
  type SurveyListItem, type SurveyCreatePayload,
} from "~/modules/survey/api/surveys"

type QuestionDraft = {
  text: string
  question_type: string
  options: { text: string }[]
}

type SurveyDraft = {
  title: string
  description: string
  is_mandatory: boolean
  questions: QuestionDraft[]
}

const emptyDraft = (): SurveyDraft => ({
  title: "", description: "", is_mandatory: false,
  questions: [{ text: "", question_type: "single", options: [{ text: "" }] }],
})

export default function AdminSurveys() {
  const { user } = useUser()
  const [surveys, setSurveys] = useState<SurveyListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [draft, setDraft] = useState<SurveyDraft>(emptyDraft())
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadSurveys = async () => {
    try {
      const data = await getSurveys()
      setSurveys(data)
    } catch {} finally { setLoading(false) }
  }

  useEffect(() => { if (user.isAuthorized) loadSurveys() }, [user.isAuthorized])

  if (!user.isAuthorized) {
    return <div className="flex h-full items-center justify-center"><p className="text-sm text-[#C5CBD3]">Требуется авторизация</p></div>
  }

  const handleNew = () => {
    setDraft(emptyDraft())
    setEditingId(null)
    setShowForm(true)
    setError(null)
  }

  const handleSave = async () => {
    if (!draft.title.trim()) { setError("Укажите название"); return }
    if (draft.questions.some((q) => !q.text.trim())) { setError("Заполните все вопросы"); return }
    const noOptions = draft.questions.find((q) => q.question_type !== "text" && q.options.filter((o) => o.text.trim()).length === 0)
    if (noOptions) { setError("Добавьте хотя бы один вариант ответа для каждого вопроса с выбором"); return }

    setSaving(true)
    setError(null)
    try {
      const payload: SurveyCreatePayload = {
        title: draft.title,
        description: draft.description || undefined,
        is_mandatory: draft.is_mandatory,
        questions: draft.questions.map((q, qi) => ({
          text: q.text,
          question_type: q.question_type,
          order: qi,
          options: q.options.filter((o) => o.text.trim()).map((o, oi) => ({ text: o.text, order: oi })),
        })),
      }

      if (editingId) {
        await updateSurveyAdmin(editingId, payload)
      } else {
        await createSurveyAdmin(payload)
      }

      setShowForm(false)
      await loadSurveys()
    } catch (err: any) {
      setError(err.response?.data?.detail || "Ошибка сохранения")
    } finally {
      setSaving(false)
    }
  }

  const handleEdit = async (id: string) => {
    try {
      const detail = await getSurvey(id)
      setDraft({
        title: detail.title,
        description: detail.description || "",
        is_mandatory: detail.is_mandatory,
        questions: detail.questions.map((q) => ({
          text: q.text,
          question_type: q.question_type,
          options: q.options.length > 0 ? q.options.map((o) => ({ text: o.text })) : [{ text: "" }],
        })),
      })
      setEditingId(id)
      setShowForm(true)
      setError(null)
    } catch (err: any) {
      setError(err.response?.data?.detail || "Не удалось загрузить опрос")
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm("Удалить опрос?")) return
    try {
      await deleteSurveyAdmin(id)
      setSurveys((prev) => prev.filter((s) => s.id !== id))
    } catch (err: any) {
      setError(err.response?.data?.detail || "Ошибка удаления")
    }
  }

  const updateQuestion = (idx: number, patch: Partial<QuestionDraft>) => {
    setDraft((prev) => ({
      ...prev,
      questions: prev.questions.map((q, i) => i === idx ? { ...q, ...patch } : q),
    }))
  }

  const addQuestion = () => {
    setDraft((prev) => ({
      ...prev,
      questions: [...prev.questions, { text: "", question_type: "single", options: [{ text: "" }] }],
    }))
  }

  const removeQuestion = (idx: number) => {
    setDraft((prev) => ({
      ...prev,
      questions: prev.questions.filter((_, i) => i !== idx),
    }))
  }

  const addOption = (qIdx: number) => {
    updateQuestion(qIdx, {
      options: [...draft.questions[qIdx].options, { text: "" }],
    })
  }

  const updateOption = (qIdx: number, oIdx: number, text: string) => {
    const newOptions = draft.questions[qIdx].options.map((o, i) => i === oIdx ? { text } : o)
    updateQuestion(qIdx, { options: newOptions })
  }

  const removeOption = (qIdx: number, oIdx: number) => {
    updateQuestion(qIdx, {
      options: draft.questions[qIdx].options.filter((_, i) => i !== oIdx),
    })
  }

  const inputCls = "w-full rounded-lg border border-[#C5CBD3] px-3 py-2 text-sm outline-none focus:border-[#3649F9] dark:border-gray-600 dark:bg-[#1e293b] dark:text-gray-200"

  if (showForm) {
    return (
      <div className="mx-auto max-w-3xl p-8">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">{editingId ? "Редактирование" : "Новый опрос"}</h1>
          <button onClick={() => setShowForm(false)} className="text-sm text-[#C5CBD3] hover:text-gray-600">Отмена</button>
        </div>

        <div className="space-y-6">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-600">Название</label>
            <input value={draft.title} onChange={(e) => setDraft((p) => ({ ...p, title: e.target.value }))} className={inputCls} />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-600">Описание</label>
            <textarea value={draft.description} onChange={(e) => setDraft((p) => ({ ...p, description: e.target.value }))}
              className={inputCls + " min-h-[60px] resize-none"} />
          </div>
          <label className="flex items-center gap-2 text-sm text-gray-600">
            <input type="checkbox" checked={draft.is_mandatory} onChange={(e) => setDraft((p) => ({ ...p, is_mandatory: e.target.checked }))} />
            Обязательный опрос
          </label>

          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-bold text-gray-800">Вопросы</h2>
              <button onClick={addQuestion} className="text-xs text-[#3649F9] hover:underline">+ Добавить вопрос</button>
            </div>

            {draft.questions.map((q, qi) => (
              <div key={qi} className="rounded-xl border border-gray-100 p-5">
                <div className="mb-3 flex items-start gap-2">
                  <span className="mt-2 text-sm font-medium text-[#3649F9]">{qi + 1}.</span>
                  <input value={q.text} onChange={(e) => updateQuestion(qi, { text: e.target.value })}
                    placeholder="Текст вопроса" className={inputCls + " flex-1"} />
                  <select value={q.question_type} onChange={(e) => updateQuestion(qi, { question_type: e.target.value })}
                    className="rounded-lg border border-[#C5CBD3] px-2 py-2 text-xs outline-none">
                    <option value="single">Один ответ</option>
                    <option value="multi">Несколько</option>
                    <option value="text">Текст</option>
                  </select>
                  {draft.questions.length > 1 && (
                    <button onClick={() => removeQuestion(qi)} className="mt-2 text-xs text-red-400 hover:text-red-500">&times;</button>
                  )}
                </div>

                {q.question_type !== "text" && (
                  <div className="ml-6 space-y-2">
                    {q.options.map((o, oi) => (
                      <div key={oi} className="flex items-center gap-2">
                        <div className="h-3 w-3 rounded-full border border-[#C5CBD3]" />
                        <input value={o.text} onChange={(e) => updateOption(qi, oi, e.target.value)}
                          placeholder={`Вариант ${oi + 1}`}
                          className="flex-1 rounded border border-gray-100 px-3 py-1.5 text-xs outline-none focus:border-[#3649F9]" />
                        {q.options.length > 1 && (
                          <button onClick={() => removeOption(qi, oi)} className="text-xs text-red-400">&times;</button>
                        )}
                      </div>
                    ))}
                    <button onClick={() => addOption(qi)} className="ml-5 text-xs text-[#3649F9] hover:underline">+ Вариант</button>
                  </div>
                )}
              </div>
            ))}
          </div>

          {error && <p className="text-sm text-red-500">{error}</p>}

          <button onClick={handleSave} disabled={saving}
            className="rounded-lg bg-[#3649F9] px-8 py-3 text-sm font-medium text-white hover:bg-[#3649F9]/90 disabled:opacity-50">
            {saving ? "Сохранение..." : editingId ? "Сохранить изменения" : "Сохранить"}
          </button>
        </div>
      </div>
    )
  }

  if (loading) return <div className="flex h-full items-center justify-center"><p className="text-sm text-[#C5CBD3]">Загрузка...</p></div>

  return (
    <div className="mx-auto max-w-3xl p-8">
      <div className="mb-8 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Управление опросами</h1>
        <button onClick={handleNew}
          className="rounded-lg bg-[#3649F9] px-4 py-2 text-sm font-medium text-white hover:bg-[#3649F9]/90">
          + Создать опрос
        </button>
      </div>

      {error && <p className="mb-4 text-sm text-red-500">{error}</p>}

      {surveys.length === 0 ? (
        <p className="text-sm text-[#C5CBD3]">Опросов пока нет. Создайте первый.</p>
      ) : (
        <div className="space-y-3">
          {surveys.map((s) => (
            <div key={s.id} className="flex items-center justify-between rounded-xl border border-gray-100 p-4 dark:border-gray-700 dark:bg-[#1e293b]">
              <div>
                <div className="flex items-center gap-2">
                  <p className="text-sm font-medium text-gray-800 dark:text-gray-200">{s.title}</p>
                  {s.is_mandatory && <span className="rounded bg-red-50 px-2 py-0.5 text-xs text-red-500">Обяз.</span>}
                </div>
                {s.description && <p className="mt-0.5 text-xs text-[#6D7C90]">{s.description}</p>}
              </div>
              <div className="flex items-center gap-2">
                <button onClick={() => handleEdit(s.id)}
                  className="rounded px-3 py-1 text-xs text-[#3649F9] hover:bg-[#E8EAFF]">
                  Редактировать
                </button>
                <button onClick={() => handleDelete(s.id)}
                  className="rounded px-3 py-1 text-xs text-red-400 hover:bg-red-50 hover:text-red-500">
                  Удалить
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
