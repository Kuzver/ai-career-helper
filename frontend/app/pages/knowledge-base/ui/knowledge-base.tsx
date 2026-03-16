import { useState } from "react"

type Card = { id: string; title: string; description: string }

const CARDS: Card[] = [
  { id: "1", title: "Как составить резюме", description: "Резюме — это ваша визитная карточка для работодателя. Укажите контактные данные, опыт работы в обратном хронологическом порядке, ключевые навыки и образование. Используйте конкретные цифры и достижения вместо общих фраз. Адаптируйте резюме под каждую вакансию, выделяя релевантный опыт." },
  { id: "2", title: "Подготовка к собеседованию", description: "Изучите компанию и вакансию заранее. Подготовьте ответы на типичные вопросы: расскажите о себе, почему хотите работать у нас, ваши сильные и слабые стороны. Используйте метод STAR для описания опыта (Ситуация, Задача, Действие, Результат). Подготовьте свои вопросы к работодателю." },
  { id: "3", title: "Построение карьерного пути", description: "Определите свои долгосрочные карьерные цели и разбейте их на этапы. Регулярно оценивайте свой прогресс и корректируйте план. Развивайте как hard skills, так и soft skills. Нетворкинг и менторство могут значительно ускорить карьерный рост." },
  { id: "4", title: "Навыки для IT-специалиста", description: "Современный IT-специалист должен владеть не только техническими навыками, но и уметь работать в команде, управлять временем и коммуницировать. Изучайте Git, основы DevOps, методологии Agile/Scrum. Постоянно обновляйте знания — технологии меняются быстро." },
  { id: "5", title: "Как вести себя на новой работе", description: "Первые 90 дней критически важны. Слушайте больше, чем говорите. Знакомьтесь с коллегами и корпоративной культурой. Задавайте вопросы — это показывает заинтересованность. Фиксируйте свои достижения с первого дня для будущих обзоров эффективности." },
  { id: "6", title: "Фриланс vs Офис", description: "Фриланс даёт свободу графика и выбора проектов, но требует самодисциплины и навыков самопродвижения. Офисная работа обеспечивает стабильность, социальные гарантии и командную среду. Гибридный формат сочетает преимущества обоих подходов. Выбирайте исходя из своих приоритетов." },
]

export default function KnowledgeBase() {
  const [selectedCard, setSelectedCard] = useState<Card | null>(null)

  return (
    <div className="p-8">
      {selectedCard && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 p-4" onClick={() => setSelectedCard(null)}>
          <div className="w-full max-w-lg rounded-3xl bg-white p-8 shadow-xl" onClick={(e) => e.stopPropagation()}>
            <h2 className="mb-3 text-xl font-semibold text-gray-900">{selectedCard.title}</h2>
            <p className="text-sm leading-relaxed text-gray-500">{selectedCard.description}</p>
            <button onClick={() => setSelectedCard(null)} className="mt-6 text-sm text-[#0157FF] hover:underline">Закрыть</button>
          </div>
        </div>
      )}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {CARDS.map((card) => (
          <button key={card.id} onClick={() => setSelectedCard(card)}
            className="rounded-2xl border border-gray-200 bg-white p-6 text-left transition-shadow hover:shadow-md">
            <h3 className="mb-2 text-base font-semibold text-gray-900">{card.title}</h3>
            <p className="line-clamp-3 text-sm leading-relaxed text-[#C5CBD3]">{card.description}</p>
          </button>
        ))}
      </div>
    </div>
  )
}
