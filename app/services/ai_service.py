from fastapi import HTTPException

from alembic.environment import Optional
from openai import OpenAI
from pydantic import BaseModel

from app.core.config import settings


client = OpenAI(
    base_url=settings.ai.base_url,
    api_key=settings.ai.api_key
)

class TicketForm(BaseModel):
    subject: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    tags: list[str] = []

class RequestData(BaseModel):
    text: str
    
class AIService:
    async def auto_fill(self, data: RequestData):
        prompt = f"""
        Извлеки данные из текста для заполнения формы. В subject добавь описание от себя абсолютно любое
        Верни ТОЛЬКО чистый JSON.
        Текст: {data.text}
        Поля: subject, priority (low, medium, high), category, tags (массив строк).
        """

        try:
            response = client.chat.completions.create(
                model="deepseek/deepseek-v4-flash:free",
                messages=[
                    {"role": "system", "content": "Ты — помощник по заполнению форм. Отвечай только валидным JSON."},
                    {"role": "user", "content": prompt}
                ],
                extra_headers={
                    "HTTP-Referer": "http://localhost:8000", 
                    "X-Title": "FastAPI Form Filler",
                }
            )
            
            result_content = response.choices[0].message.content
            return TicketForm.model_validate_json(result_content)
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка нейросети: {str(e)}")
        
def ai_service_getter(
) -> AIService:
    return AIService()