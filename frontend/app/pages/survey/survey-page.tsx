import { useEffect, useRef, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { getSurvey, submitSurvey, getMyAnswers, type SurveyDetail, type SubmitAnswer } from "~/modules/survey/api/surveys"
import { useUser } from "~/modules/user/lib/use-user"

export default function SurveyPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user } = useUser()

  const [survey, setSurvey] = useState<SurveyDetail | null>(null)
  const [answers, setAnswers] = useState<Record<string, SubmitAnswer>>({})
  const [submitting, setSubmitting] = useState(false)
  const [validationResult, setValidationResult] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [isEdit, setIsEdit] = useState(false)
  const questionRefs = useRef<Record<string, HTMLDivElement | null>>({})

  useEffect(() => {
    if (!id) return
    const load = async () => {
      try {
        const s = await getSurvey(id)
        setSurvey(s)
        const prev = await getMyAnswers(id)
        if (prev.length > 0) {
          const map: Record<string, SubmitAnswer> = {}
          for (const a of prev) {
            map[String(a.question_id)] = a
          }
          setAnswers(map)
          setIsEdit(true)
        }
      } catch {
        setLoadError("Опрос не найден")
      }
      setLoading(false)
    }
    load()
  }, [id])

  if (!user.isAuthorized) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-sm text-[#C5CBD3]">Войдите, чтобы пройти опрос</p>
      </div>
    )
  }

  if (loading) return <div className="flex h-full items-center justify-center"><p className="text-sm text-[#C5CBD3]">Загрузка...</p></div>
  if (loadError) return <div className="flex h-full items-center justify-center"><p className="text-sm text-red-500">{loadError}</p></div>
  if (!survey) return null

  const handleOptionSelect = (questionId: string, optionId: string) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: { question_id: questionId, option_id: optionId },
    }))
    setError(null)
  }

  const handleTextAnswer = (questionId: string, text: string) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: { question_id: questionId, free_text: text },
    }))
    setError(null)
  }

  const handleSubmit = async () => {
    const unanswered = survey.questions.filter(
      (q) => q.is_required && !answers[q.id]
    )
    if (unanswered.length > 0) {
      setError(`Ответьте на все вопросы (осталось: ${unanswered.length})`)
      const firstId = unanswered[0].id
      questionRefs.current[firstId]?.scrollIntoView({ behavior: "smooth", block: "center" })
      return
    }

    // Добавляем пустые текстовые ответы если не заполнены
    const finalAnswers: SubmitAnswer[] = survey.questions.map((q) => {
      if (answers[q.id]) return answers[q.id]
      return { question_id: q.id, free_text: "" }
    })

    setSubmitting(true)
    setError(null)
    try {
      const result = await submitSurvey(survey.id, finalAnswers)
      setValidationResult(result.validation_result)
    } catch (err: any) {
      const detail = err.response?.data?.detail
      setError(typeof detail === "string" ? detail : "Не удалось отправить. Попробуйте позже.")
    } finally {
      setSubmitting(false)
    }
  }

  if (validationResult !== null) {
    return (
      <div className="mx-auto max-w-2xl p-8">
        <div className="rounded-2xl border border-green-200 bg-green-50 p-8 text-center dark:border-green-800 dark:bg-green-950">
          <div className="mb-4 text-4xl">&#10003;</div>
          <h2 className="mb-3 text-xl font-bold text-gray-900 dark:text-gray-100">Спасибо за прохождение опроса!</h2>
          <p className="mb-6 text-sm text-gray-600 dark:text-gray-400">Ваши ответы сохранены и будут учитываться при рекомендациях. Перейдите в чат — ИИ-ассистент поможет вам достичь вашей цели.</p>
          <div className="flex justify-center gap-3">
            <button onClick={() => navigate("/chat")} className="rounded-lg bg-[#3649F9] px-6 py-2.5 text-sm font-medium text-white hover:bg-[#3649F9]/90">Перейти в чат</button>
            <button onClick={() => navigate("/surveys")} className="rounded-lg border border-gray-200 px-6 py-2.5 text-sm font-medium text-gray-600 hover:bg-gray-50 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-gray-800">К опросам</button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-2xl p-8">
      <h1 className="mb-2 text-2xl font-bold text-gray-900 dark:text-gray-100">{survey.title}</h1>
      {survey.description && <p className="mb-8 text-sm text-[#6D7C90]">{survey.description}</p>}

      <div className="space-y-8">
        {survey.questions.map((q, idx) => {
          const isUnanswered = error && q.is_required && !answers[q.id]
          return (
            <div
              key={q.id}
              ref={(el) => { questionRefs.current[q.id] = el }}
              className={[
                "rounded-xl border p-6 transition-colors",
                isUnanswered ? "border-red-300 bg-red-50/30 dark:border-red-700 dark:bg-red-900/20" : "border-gray-100 dark:border-gray-700",
              ].join(" ")}
            >
              <p className="mb-4 text-sm font-medium text-gray-800 dark:text-gray-200">
                <span className="mr-2 text-[#3649F9]">{idx + 1}.</span>
                {q.text}
                {!q.is_required && <span className="ml-2 text-xs text-[#C5CBD3]">(необязательно)</span>}
              </p>

              {q.question_type === "text" ? (
                <textarea
                  value={answers[q.id]?.free_text || ""}
                  onChange={(e) => handleTextAnswer(q.id, e.target.value)}
                  placeholder="Ваш ответ..."
                  className="w-full rounded-lg border border-[#C5CBD3] px-4 py-3 text-sm outline-none placeholder-[#C5CBD3] focus:border-[#3649F9] min-h-[80px] resize-none dark:border-gray-600 dark:bg-[#1e293b] dark:text-gray-200"
                />
              ) : (
                <div className="space-y-2">
                  {q.options.map((o) => {
                    const selected = answers[q.id]?.option_id === o.id
                    return (
                      <button
                        key={o.id}
                        onClick={() => handleOptionSelect(q.id, o.id)}
                        className={[
                          "block w-full rounded-lg border px-4 py-3 text-left text-sm transition-colors",
                          selected
                            ? "border-[#3649F9] bg-[#E8EAFF] text-[#3649F9] dark:bg-[#3649F9]/20"
                            : "border-gray-100 text-gray-600 hover:border-[#C5CBD3] dark:border-gray-700 dark:text-gray-300",
                        ].join(" ")}
                      >
                        {o.text}
                      </button>
                    )
                  })}
                </div>
              )}
            </div>
          )
        })}
      </div>

      {error && <p className="mt-4 text-sm text-red-500">{error}</p>}

      <div className="mt-8 flex items-center gap-4 pb-8">
        <button onClick={handleSubmit} disabled={submitting}
          className="rounded-lg bg-[#3649F9] px-8 py-3 text-sm font-medium text-white hover:bg-[#3649F9]/90 disabled:opacity-50">
          {submitting ? "Отправка..." : isEdit ? "Обновить ответы" : "Отправить ответы"}
        </button>
        {isEdit && (
          <span className="text-xs text-[#6D7C90]">Вы можете изменить ответы и отправить заново</span>
        )}
      </div>
    </div>
  )
}
