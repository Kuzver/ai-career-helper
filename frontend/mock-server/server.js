import express from "express"
import cors from "cors"
import { readFile, writeFile } from "node:fs/promises"
import { randomUUID } from "node:crypto"
import path from "node:path"
import { fileURLToPath } from "node:url"

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const DB_PATH = path.join(__dirname, "users.json")

const app = express()
const PORT = process.env.MOCK_AUTH_PORT ?? 4000

app.use(cors())
app.use(express.json())

const readUsers = async () => {
  try {
    const data = await readFile(DB_PATH, "utf-8")
    return JSON.parse(data)
  } catch (error) {
    if (error.code === "ENOENT") {
      await writeFile(DB_PATH, "[]", "utf-8")
      return []
    }
    throw error
  }
}

const writeUsers = async (users) => {
  await writeFile(DB_PATH, JSON.stringify(users, null, 2), "utf-8")
}

app.post("/api/login", async (req, res) => {
  const { applicationId, loginId, password } = req.body || {}

  if (!applicationId || !loginId || !password) {
    return res
      .status(400)
      .json({ message: "applicationId, loginId и password являются обязательными" })
  }

  const users = await readUsers()
  const user = users.find(
    (u) => u.email === loginId && u.applicationId === applicationId,
  )

  if (!user || user.password !== password) {
    return res.status(401).json({ message: "Неверный email или пароль" })
  }

  return res.json({
    token: `mock-token-${randomUUID()}`,
    user: {
      id: user.id,
      email: user.email,
    },
  })
})

app.post("/api/user/registration", async (req, res) => {
  const { user, registration } = req.body || {}
  const email = user?.email
  const password = user?.password
  const applicationId = registration?.applicationId

  if (!email || !password || !applicationId) {
    return res
      .status(400)
      .json({ message: "email, password и applicationId являются обязательными" })
  }

  const users = await readUsers()
  const alreadyExists = users.some((u) => u.email === email)

  if (alreadyExists) {
    return res.status(409).json({ message: "Пользователь с таким email уже существует" })
  }

  const newUser = {
    id: randomUUID(),
    email,
    password,
    applicationId,
  }

  users.push(newUser)
  await writeUsers(users)

  return res.status(201).json({
    user: {
      id: newUser.id,
      email: newUser.email,
    },
    token: `mock-token-${randomUUID()}`,
  })
})

app.listen(PORT, () => {
  console.log(`Mock auth server is running at http://localhost:${PORT}`)
})
