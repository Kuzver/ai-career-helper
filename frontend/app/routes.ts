import { type RouteConfig, index, layout, route } from "@react-router/dev/routes"

export default [
  layout("shared/components/ui/app-layout.tsx", [
    index("pages/chat.tsx"),
    route("knowledge-base", "pages/knowledge-base/ui/knowledge-base.tsx"),
  ]),
  layout("pages/auth/ui/auth-layout.tsx", [
    route("sign-in", "pages/auth/ui/sign-in.tsx"),
    route("sign-up", "pages/auth/ui/sign-up.tsx"),
  ]),
] satisfies RouteConfig
