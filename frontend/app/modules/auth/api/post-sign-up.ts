import axios from "axios"
import { authClient } from "~/shared/api/axios-client"
import type { signUpSchemaFields } from "../model/schema"
import { env } from "~/shared/config/env"

export const postSignUp = async ({ email, password }: signUpSchemaFields) => {
  try {
    const response = await authClient.post("user/registration", {
      user: {
        email,
        password,
      },
      registration: {
        applicationId: env.authAppId,
      },
    })

    return response
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const message =
        (error.response?.data as { message?: string } | undefined)?.message ||
        error.message ||
        "Произошла непредвиденная ошибка"
      throw new Error(message)
    }

    throw new Error("Произошла непредвиденная ошибка")
  }
}
