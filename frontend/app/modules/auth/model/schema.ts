import { z } from "zod"

const passwordSchema = z
  .string()
  .min(8, "Пароль должен содержать минимум 8 символов")
  .regex(/[A-Z]/, "Добавьте хотя бы одну заглавную букву")
  .regex(/\d/, "Добавьте хотя бы одну цифру")

export const signInSchema = z.object({
  email: z.email("Введите корректный email"),
  password: passwordSchema,
})

export const signUpSchema = signInSchema
  .extend({
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    path: ["confirmPassword"],
    message: "Пароли должны совпадать",
  })

export type signInSchemaFields = z.infer<typeof signInSchema>
export type signUpSchemaFields = z.infer<typeof signUpSchema>
