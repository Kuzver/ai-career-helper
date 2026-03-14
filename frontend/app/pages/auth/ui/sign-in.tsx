import { Controller, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link, useFetcher, useNavigate } from "react-router"
import {
  Field,
  FieldDescription,
  FieldGroup,
  FieldLabel,
  FieldLegend,
  FieldSet,
  FieldError,
} from "~/shared/components/ui/field";
import { Input } from "~/shared/components/ui/input";
import { Button } from "~/shared/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "~/shared/components/ui/card";
import type { Route } from "../ui/+types/sign-in";
import { signInSchema, type signInSchemaFields } from "~/modules/auth/model/schema";
import { postSignIn } from "~/modules/auth/api/post-sign-in";
import { useEffect } from "react";
import { useUser } from "~/modules/user/lib/use-user";




export async function clientAction(args: Route.ActionArgs) {
  //TODO обработка ошибок
  try {
    const authData = Object.fromEntries(
      await args.request.formData(),
    ) as signInSchemaFields
    const response = await postSignIn(authData)

    return { user: response.data.user }
  } catch (error) {
    const message =
      error instanceof Error
        ? error.message
        : "Произошла непредвиденная ошибка"

    return { error: message }
  }
}

export default function SignIn() {
  const { handleSubmit, control } = useForm<signInSchemaFields>({
    resolver: zodResolver(signInSchema),
    defaultValues: {
      email: "",
      password: "",
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

  function onSubmit(data: signInSchemaFields) {
    fetcher.submit(data, { method: "post" })
  }

  return (
    <section className="min-h-[calc(100vh-120px)] bg-linear-to-b from-muted/40 via-background to-background py-16">
      <div className="container mx-auto flex max-w-5xl flex-col items-center gap-10 px-4 text-center">
        <div className="space-y-3">
          <p className="text-sm font-medium uppercase tracking-[0.35em] text-primary/80">
            Добро пожаловать!
          </p>
          <h1 className="text-pretty text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
            Войдите, чтобы продолжить работу с AI Career Helper
          </h1>
        </div>

        <Card className="w-full max-w-xl text-left shadow-lg shadow-primary/5">
          <CardHeader>
            <CardTitle>Вход в аккаунт</CardTitle>
            <CardDescription>
              Введите свои данные, чтобы попасть в рабочее пространство.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
              <FieldSet className="space-y-6">
                <FieldLegend className="sr-only">Форма входа</FieldLegend>
                <FieldGroup>
                  <Controller
                    name="email"
                    control={control}
                    render={({ field, fieldState }) => (
                      <Field data-invalid={fieldState.invalid}>
                        <FieldLabel htmlFor="sign-in-email">Email</FieldLabel>
                        <Input
                          {...field}
                          id="sign-in-email"
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
                        <FieldLabel htmlFor="sign-in-password">
                          Пароль
                        </FieldLabel>
                        <FieldDescription>
                          Минимум 8 символов, одна цифра и заглавная буква.
                        </FieldDescription>
                        <Input
                          {...field}
                          id="sign-in-password"
                          aria-invalid={fieldState.invalid}
                          placeholder="Введите пароль"
                          type="password"
                          autoComplete="current-password"
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
                <p className="text-sm text-destructive">{fetcher.data.error}</p>
              )}
              <Button
                type="submit"
                className="w-full"
                disabled={fetcher.state === "submitting"}
              >
                Войти в аккаунт
              </Button>
            </form>
          </CardContent>
          <CardFooter className="flex flex-col gap-2 text-sm text-muted-foreground">
            <p>
              Нет аккаунта?{" "}
              <Link
                to="/sign-up"
                className="font-medium text-primary underline-offset-4 hover:underline"
              >
                Зарегистрироваться
              </Link>
            </p>
            {/* <p>
              Нужна помощь?{" "}
              <a
                href="#"
                className="font-medium text-primary underline-offset-4 hover:underline"
              >
                Связаться с поддержкой
              </a>
            </p> */}
          </CardFooter>
        </Card>
      </div>
    </section>
  )
}
