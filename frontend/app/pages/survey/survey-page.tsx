import { useEffect, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { getSurvey, submitSurvey, type SurveyDetail, type SubmitAnswer } from "~/modules/survey/api/surveys"
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
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return
    getSurvey(id)
      .then(setSurvey)
      .catch(() => setError("Опрос не найден"))
      .finally(() => setLoading(false))
  }, [id])

  if (!user.isAuthorized) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-sm text-[#C5CBD3]">Войдите, чтобы пройти опрос</p>
      </div>
    )
  }

  if (loading) return <div className="flex h-full items-center justify-center"><p className="text-sm text-[#C5CBD3]">Загрузка...</p></div>
  if (error) return <div className="flex h-full items-center justify-center"><p className="text-sm text-red-500">{error}</p></div>
  if (!survey) return null

  const handleOptionSelect = (questionId: string, optionId: string, type: string) => {
    setAnswers((prev) => {
      if (type === "multi") {
        const existing = prev[questionId]
        if (existing?.option_id === optionId) {
          const { [questionId]: _, ...rest } = prev
          return rest
        }
      }
      return { ...prev, [questionId]: { question_id: questionId, option_id: optionId } }
    })
  }

  const handleTextAnswer = (questionId: string, text: string) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: { question_id: questionId, free_text: text },
    }))
  }

  const handleSubmit = async () => {
    const unanswered = survey.questions.filter((q) => !answers[q.id])
    if (unanswered.length > 0) {
      setError(`Ответьте на все вопросы (осталось: ${unanswered.length})`)
      return
    }

    setSubmitting(true)
    setError(null)
    try {
      const result = await submitSurvey(survey.id, Object.values(answers))
      setValidationResult(result.validation_result)
    } catch (err: any) {
      setError(err.response?.data?.detail || "Не удалось отправить")
    } finally {
      setSubmitting(false)
    }
  }

  if (validationResult) {
    return (
      <div className="mx-auto max-w-2xl p-8">
        <div className="rounded-2xl border border-green-200 bg-green-50 p-8 text-center">
          <div className="mb-4 text-3xl">&#10003;</div>
          <h2 className="mb-4 text-xl font-bold text-gray-900">Опрос пройден</h2>
          <p className="mb-6 text-sm text-gray-600">{validationResult}</p>
          <button onClick={() => navigate("/chat")}
            className="rounded-lg bg-[#3649F9] px-6 py-2.5 text-sm font-medium text-white hover:bg-[#3649F9]/90">
            Перейти к чату
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-2xl p-8">
      <h1 className="mb-2 text-2xl font-bold text-gray-900">{survey.title}</h1>
      {survey.description && <p className="mb-8 text-sm text-[#6D7C90]">{survey.description}</p>}

      <div className="space-y-8">
        {survey.questions.map((q, idx) => (
          <div key={q.id} className="rounded-xl border border-gray-100 p-6">
            <p className="mb-4 text-sm font-medium text-gray-800">
              <span className="mr-2 text-[#3649F9]">{idx + 1}.</span>
              {q.text}
            </p>

            {q.question_type === "text" ? (
              <textarea
                value={answers[q.id]?.free_text || ""}
                onChange={(e) => handleTextAnswer(q.id, e.target.value)}
                placeholder="Ваш ответ..."
                className="w-full rounded-lg border border-[#C5CBD3] px-4 py-3 text-sm outline-none placeholder-[#C5CBD3] focus:border-[#3649F9]"
              />
            ) : (
              <div className="space-y-2">
                {q.options.map((o) => {
                  const selected = answers[q.id]?.option_id === o.id
                  return (
                    <button
                      key={o.id}
                      onClick={() => handleOptionSelect(q.id, o.id, q.question_type)}
                      className={[
                        "block w-full rounded-lg border px-4 py-3 text-left text-sm transition-colors",
                        selected
                          ? "border-[#3649F9] bg-[#E8EAFF] text-[#3649F9]"
                          : "border-gray-100 text-gray-600 hover:border-[#C5CBD3]",
                      ].join(" ")}
                    >
                      {o.text}
                    </button>
                  )
                })}
              </div>
            )}
          </div>
        ))}
      </div>

      {error && <p className="mt-4 text-sm text-red-500">{error}</p>}

      <div className="mt-8">
        <button onClick={handleSubmit} disabled={submitting}
          className="rounded-lg bg-[#3649F9] px-8 py-3 text-sm font-medium text-white hover:bg-[#3649F9]/90 disabled:opacity-50">
          {submitting ? "Отправка..." : "Отправить ответы"}
        </button>
      </div>
    </div>
  )
}
