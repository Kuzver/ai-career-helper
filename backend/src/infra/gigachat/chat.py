from asyncio import timeout
from typing import Dict, Any, List, Optional
from gigachat import GigaChat, GigaChatAsyncClient
from gigachat.models import Chat, Messages, MessagesRole
from src.main.config import config
from loguru import logger


class Gigachat:
    def __init__(self,):
        self.model = GigaChatAsyncClient(credentials=config.gigachat.authorization_key, verify_ssl_certs=False)

    async def __call__(self, user_query: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        if history:
            hist_text = ""
            # Берём только последние N сообщений, чтобы не раздуть контекст
            for msg in history[-10:]:
                role = "Пользователь" if msg["role"] == "user" else "Ассистент"
                hist_text += f"{role}: {msg['content']}\n"

            prompt = (
                f"{hist_text}\n"
                f"Пользователь: {user_query}\n"
                f"Ассистент:"
            )
        else:
            prompt = user_query
        logger.info(33)
        messages = []
        messages.append(Messages(role=MessagesRole.USER, content=prompt))


        resp = await self.model.achat(
            Chat(messages=messages),
        )
        logger.info(resp)

        return resp.choices[0].message.content