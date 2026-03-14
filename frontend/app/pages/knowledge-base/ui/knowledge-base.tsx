import { Link, useLoaderData } from "react-router"

import type { Route } from "./+types/knowledge-base"
import { getKnowledgeBaseCards } from "~/modules/knowledge-base/api/get-cards"
import type { KnowledgeBaseCollection } from "~/modules/knowledge-base/model/types"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "~/shared/components/ui/accordion"
import { Button } from "~/shared/components/ui/button"

const COLLECTION_FETCH_LIMIT = 50
const CARDS_PER_PAGE = 6

type FlatCard = {
  id: string
  title: string
  description: string
  category: string
  createdAt: string
}

const truncate = (text: string) => {
  if (text.length <= 140) return text
  return `${text.slice(0, 137)}...`
}

const flattenCards = (collections: KnowledgeBaseCollection[]): FlatCard[] => {
  return collections.flatMap((collection) =>
    collection.cards.map((card) => ({
      id: card.id,
      title: card.title,
      description: card.description,
      category: collection.title,
      createdAt: card.createdAt,
    })),
  )
}

export async function clientLoader({ request }: Route.ClientLoaderArgs) {
  const url = new URL(request.url)
  const pageParam = Number(url.searchParams.get("page") ?? "1")
  const rawPage = Number.isNaN(pageParam) || pageParam < 1 ? 1 : pageParam

  const data = await getKnowledgeBaseCards({
    limit: COLLECTION_FETCH_LIMIT,
    offset: 0,
  })

  const cards = flattenCards(data.items)
  const totalCards = cards.length
  const totalPages = Math.max(1, Math.ceil(totalCards / CARDS_PER_PAGE))
  const page = Math.min(rawPage, totalPages)
  const startIndex = (page - 1) * CARDS_PER_PAGE
  const pageCards = cards.slice(startIndex, startIndex + CARDS_PER_PAGE)

  return {
    cards: pageCards,
    page,
    totalCards,
    totalPages,
  }
}

export default function KnowledgeBase() {
  const { cards, page, totalCards, totalPages } = useLoaderData<typeof clientLoader>()
  const from = cards.length ? (page - 1) * CARDS_PER_PAGE + 1 : 0
  const to = cards.length ? from + cards.length - 1 : 0
  const hasPrev = page > 1
  const hasNext = page < totalPages

  return (
    <div className="space-y-8">
      <header className="space-y-2">
        <p className="text-sm uppercase tracking-[0.35em] text-primary/70">Knowledge base</p>
        <h1 className="text-3xl font-semibold tracking-tight">Полезные материалы для развития карьеры</h1>
        <p className="text-muted-foreground">
          Изучайте карточки с советами и практическими рекомендациями, которые мы подготовили специально для вашей
          команды.
        </p>
      </header>

      {cards.length === 0 ? (
        <div className="rounded-xl border border-dashed p-10 text-center">
          <h2 className="text-xl font-semibold">Пока что здесь пусто</h2>
          <p className="text-muted-foreground">
            Как только появятся карточки, вы сможете изучать материалы и сохранять заметки.
          </p>
        </div>
      ) : (
        <Accordion type="multiple" className="space-y-4">
          {cards.map((card) => (
            <AccordionItem
              key={card.id}
              value={card.id}
              className="rounded-3xl border border-border/60 bg-card shadow-sm px-4"
            >
              <AccordionTrigger className="py-5">
                <div className="flex flex-col text-left">
                  <span className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                    {card.category}
                  </span>
                  <span className="text-base font-semibold text-foreground">{card.title}</span>
                  <span className="text-sm text-muted-foreground">{truncate(card.description)}</span>
                </div>
              </AccordionTrigger>
              <AccordionContent className="px-1 pb-5 text-sm leading-relaxed text-muted-foreground">
                {card.description}
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      )}

      <footer className="flex flex-col gap-4 border-t pt-4 text-sm text-muted-foreground md:flex-row md:items-center md:justify-between">
        <span>
          Показано {from}–{to} из {totalCards}
        </span>
        <div className="flex items-center gap-2">
          {hasPrev ? (
            <Button variant="outline" size="sm" asChild>
              <Link to={`?page=${page - 1}`}>Назад</Link>
            </Button>
          ) : (
            <Button variant="outline" size="sm" disabled>
              Назад
            </Button>
          )}
          <span>
            Страница {page} из {totalPages}
          </span>
          {hasNext ? (
            <Button variant="outline" size="sm" asChild>
              <Link to={`?page=${page + 1}`}>Вперед</Link>
            </Button>
          ) : (
            <Button variant="outline" size="sm" disabled>
              Вперед
            </Button>
          )}
        </div>
      </footer>
    </div>
  )
}
