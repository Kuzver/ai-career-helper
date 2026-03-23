import { type RouteConfig, index, layout, route } from "@react-router/dev/routes"

export default [
  layout("shared/components/ui/app-layout.tsx", [
    index("pages/index.tsx"),
    route("chat", "pages/chat.tsx"),
    route("knowledge-base", "pages/knowledge-base/ui/knowledge-base.tsx"),
    route("knowledge-base/:slug", "pages/knowledge-base/ui/article-page.tsx"),
    route("profile", "pages/profile.tsx"),
    route("roadmap", "pages/roadmap.tsx"),
    route("surveys", "pages/survey/survey-list.tsx"),
    route("survey/:id", "pages/survey/survey-page.tsx"),
    route("admin/surveys", "pages/admin/surveys.tsx"),
    route("admin/articles", "pages/admin/articles.tsx"),
    route("admin/users", "pages/admin/users.tsx"),
  ]),

  layout("pages/auth/ui/auth-layout.tsx", [
    route("sign-in", "pages/auth/ui/sign-in.tsx"),
    route("sign-up", "pages/auth/ui/sign-up.tsx"),
  ]),
] satisfies RouteConfig
