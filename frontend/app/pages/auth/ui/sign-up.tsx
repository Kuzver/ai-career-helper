import { Controller, useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { Link, useFetcher, useNavigate } from "react-router"
import type { Route } from "../ui/+types/sign-up"
import {
  Field,
  FieldDescription,
  FieldError,
  FieldGroup,
  FieldLabel,
  FieldLegend,
  FieldSet,
} from "~/shared/components/ui/field"
import { Input } from "~/shared/components/ui/input"
import { Button } from "~/shared/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "~/shared/components/ui/card"
import { signUpSchema, type signUpSchemaFields } from "~/modules/auth/model/schema"
import { postSignUp } from "~/modules/auth/api/post-sign-up"
import { useEffect } from "react"
import { useUser } from "~/modules/user/lib/use-user"

export async function clientAction(args: Route.ActionArgs) {
  try {
    const registrationData = Object.fromEntries(
      await args.request.formData(),
    ) as signUpSchemaFields

    const response = await postSignUp(registrationData)
    return { user: response.data.user }
  } catch (error) {
    const message =
      error instanceof Error
        ? error.message
        : "Произошла непредвиденная ошибка"

    return { error: message }
  }
}

export default function SignUp() {
  const { handleSubmit, control } = useForm<signUpSchemaFields>({
    resolver: zodResolver(signUpSchema),
    defaultValues: {
      email: "",
      password: "",
      confirmPassword: "",
    },
  })

  const fetcher = useFetcher<typeof clientAction>()
  const navigate = useNavigate()
  const { setUser } = useUser()

  useEffect(() => {
    if (fetcher.data?.user) {
      setUser({ isAuthorized: true, email: fetcher.data.user.email })
      navigate("/")
    }
  }, [fetcher.data, setUser, navigate])

  function onSubmit(data: signUpSchemaFields) {
    fetcher.submit(data, { method: "post" })
  }

  return (
    <section className="min-h-[calc(100vh-120px)] bg-muted/20 py-16">
      <div className="container mx-auto flex max-w-5xl flex-col items-center gap-10 px-4 text-center">
        <div className="space-y-3">
          <p className="text-sm font-medium uppercase tracking-[0.35em] text-primary/80">
            Присоединяйтесь к нам
          </p>
          <h1 className="text-pretty text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
            Создайте аккаунт AI Career Helper
          </h1>
          <p className="text-balance text-muted-foreground sm:text-lg">
            Создайте личный профиль и начните путь вместе с AI Career Helper.
          </p>
        </div>

        <Card className="w-full max-w-xl text-left shadow-lg shadow-primary/5">
          <CardHeader>
            <CardTitle>Регистрация</CardTitle>
            <CardDescription>
              Заполните форму, и мы создадим для вас рабочий кабинет.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
              <FieldSet className="space-y-6">
                <FieldLegend className="sr-only">Форма регистрации</FieldLegend>
                <FieldGroup>
                  <Controller
                    name="email"
                    control={control}
                    render={({ field, fieldState }) => (
                      <Field data-invalid={fieldState.invalid}>
                        <FieldLabel htmlFor="sign-up-email">Email</FieldLabel>
                        <Input
                          {...field}
                          id="sign-up-email"
                          aria-invalid={fieldState.invalid}
                          placeholder="you@some-mail.com"
                          autoComplete="email"
                        />
                        {fieldState.invalid && (
                          <FieldError errors={[fieldState.error]} />
                        )}
                      </Field>
                    )}
                  />

                  <Controller
                    name="password"
                    control={control}
                    render={({ field, fieldState }) => (
                      <Field data-invalid={fieldState.invalid}>
                        <FieldLabel htmlFor="sign-up-password">
                          Пароль
                        </FieldLabel>
                        <FieldDescription>
                          Минимум 8 символов, одна цифра и заглавная буква.
                        </FieldDescription>
                        <Input
                          {...field}
                          id="sign-up-password"
                          aria-invalid={fieldState.invalid}
                          placeholder="Введите пароль"
                          type="password"
                          autoComplete="new-password"
                        />
                        {fieldState.invalid && (
                          <FieldError errors={[fieldState.error]} />
                        )}
                      </Field>
                    )}
                  />

                  <Controller
                    name="confirmPassword"
                    control={control}
                    render={({ field, fieldState }) => (
                      <Field data-invalid={fieldState.invalid}>
                        <FieldLabel htmlFor="sign-up-confirm-password">
                          Подтверждение пароля
                        </FieldLabel>
                        <FieldDescription>
                          Повторите пароль, чтобы исключить опечатки.
                        </FieldDescription>
                        <Input
                          {...field}
                          id="sign-up-confirm-password"
                          aria-invalid={fieldState.invalid}
                          placeholder="Подтвердите пароль"
                          type="password"
                          autoComplete="new-password"
                        />
                        {fieldState.invalid && (
                          <FieldError errors={[fieldState.error]} />
                        )}
                      </Field>
                    )}
                  />
                </FieldGroup>
              </FieldSet>
              {fetcher.data?.error && (
                <p className="text-sm text-destructive">
                  {fetcher.data.error}
                </p>
              )}
              <Button type="submit" className="w-full" disabled={fetcher.state === "submitting"}>
                Создать аккаунт
              </Button>
            </form>
          </CardContent>
          <CardFooter className="flex flex-col gap-2 text-sm text-muted-foreground">
            <p>
              Уже есть аккаунт?{" "}
              <Link
                to="/sign-in"
                className="font-medium text-primary underline-offset-4 hover:underline"
              >
                Войти
              </Link>
            </p>
          </CardFooter>
        </Card>
      </div>
    </section>
  )
}
