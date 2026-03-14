import axios from "axios"
import { authClient } from "~/shared/api/axios-client"
import type { signInSchemaFields } from "../model/schema"
import { env } from "~/shared/config/env"

export const postSignIn = async ({ email, password }: signInSchemaFields) => {
  try {
    const respone = await authClient.post("login", {
      applicationId: env.authAppId,
      loginIdTypes: ["email"],
      loginId: email,
      password: password,
    })

    return respone
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
