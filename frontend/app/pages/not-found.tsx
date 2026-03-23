import { Link } from "react-router-dom"

export default function NotFoundPage() {
  return (
    <div className="flex h-screen flex-col items-center justify-center bg-white">
      <div className="mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-[#E8EAFF]">
        <span className="text-3xl font-bold text-[#3649F9]">404</span>
      </div>
      <h1 className="mb-2 text-xl font-bold text-gray-900">Страница не найдена</h1>
      <p className="mb-6 text-sm text-[#6D7C90]">Такой страницы не существует или она была удалена</p>
      <Link to="/chat" className="rounded-lg bg-[#3649F9] px-6 py-2.5 text-sm font-medium text-white hover:bg-[#3649F9]/90">
        На главную
      </Link>
    </div>
  )
}
