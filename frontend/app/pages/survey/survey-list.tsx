import { useEffect, useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { getSurveys, type SurveyListItem } from "~/modules/survey/api/surveys"
import { useUser } from "~/modules/user/lib/use-user"

export default function SurveyList() {
  const { user } = useUser()
  const navigate = useNavigate()
  const [surveys, setSurveys] = useState<SurveyListItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user.isAuthorized) return
    getSurveys()
      .then(setSurveys)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [user.isAuthorized])

  if (!user.isAuthorized) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-sm text-[#C5CBD3]">Войдите, чтобы видеть опросы</p>
      </div>
    )
  }

  if (loading) return <div className="flex h-full items-center justify-center"><p className="text-sm text-[#C5CBD3]">Загрузка...</p></div>

  return (
    <div className="mx-auto max-w-2xl p-8">
      <h1 className="mb-8 text-2xl font-bold text-gray-900 dark:text-gray-100">Опросы</h1>

      {surveys.length === 0 ? (
        <p className="text-sm text-[#C5CBD3]">Опросов пока нет</p>
      ) : (
        <div className="space-y-4">
          {surveys.map((s) => (
            <div key={s.id} className="flex items-center justify-between rounded-xl border border-gray-100 p-5 dark:border-gray-700 dark:bg-[#1e293b]">
              <div>
                <div className="flex items-center gap-2">
                  <p className="text-sm font-medium text-gray-800 dark:text-gray-200">{s.title}</p>
                  {s.is_mandatory && (
                    <span className="rounded bg-red-50 px-2 py-0.5 text-xs text-red-500">Обязательный</span>
                  )}
                  {s.is_completed && (
                    <span className="rounded bg-green-50 px-2 py-0.5 text-xs text-green-600">Пройден</span>
                  )}
                </div>
                {s.description && <p className="mt-1 text-xs text-[#6D7C90]">{s.description}</p>}
              </div>
              <div className="flex items-center gap-2">
                {s.is_completed && (
                  <button onClick={() => navigate(`/survey/${s.id}`)}
                    className="rounded-lg border border-[#3649F9] px-4 py-2 text-xs font-medium text-[#3649F9] hover:bg-[#E8EAFF]">
                    Просмотреть
                  </button>
                )}
                {!s.is_completed && (
                  <button onClick={() => navigate(`/survey/${s.id}`)}
                    className="rounded-lg bg-[#3649F9] px-4 py-2 text-xs font-medium text-white hover:bg-[#3649F9]/90">
                    Пройти
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
