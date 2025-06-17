import os
import time
import base64
import requests
import openai
import datetime
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

load_dotenv()  # Загружаем .env

# --- Константы из .env ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OAUTH_TOKEN = os.getenv("OAUTH_TOKEN")
CATALOG_ID = os.getenv("CATALOG_ID")

# --- OpenAI client ---
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# --- aiogram core ---
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- FSM для генерации картинки ---
class ImageStates(StatesGroup):
    waiting_for_prompt = State()

# --- Функция для получения IAM токена Яндекса ---
def get_iam_token(oauth_token):
    url = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
    response = requests.post(url, json={"yandexPassportOauthToken": oauth_token})
    if response.status_code == 200:
        return response.json()["iamToken"]
    else:
        raise Exception(f"Ошибка при получении IAM_TOKEN: {response.status_code} {response.text}")

# --- /start ---
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот с искусственным интеллектом.\n"
        "Напиши что-нибудь, чтобы поговорить со мной, или используй команду /image для генерации картинки."
    )

# --- /image: переходим в состояние ожидания промпта ---
@dp.message(Command("image"))
async def image_command(message: types.Message, state: FSMContext):
    await message.answer("Отправь мне описание картинки (промпт):")
    await state.set_state(ImageStates.waiting_for_prompt)

# --- Ожидание промпта и генерация картинки ---
@dp.message(ImageStates.waiting_for_prompt)
async def handle_image_prompt(message: types.Message, state: FSMContext):
    prompt = message.text
    await message.answer("⏳ Генерирую изображение...")

    try:
        # Получаем IAM токен
        iam_token = get_iam_token(OAUTH_TOKEN)
        # Готовим запрос
        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/imageGenerationAsync"
        headers = {
            "Authorization": f"Bearer {iam_token}",
            "Content-Type": "application/json"
        }
        data = {
            "modelUri": f"art://{CATALOG_ID}/yandex-art/latest",
            "generationOptions": {
                "seed": str(int(time.time())),
                "aspectRatio": {"widthRatio": "2", "heightRatio": "1"}
            },
            "messages": [{"weight": "1", "text": prompt}]
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            await message.answer(f"❌ Ошибка генерации: {response.status_code}\n{response.text}")
            await state.clear()
            return

        request_id = response.json().get("id")
        # Немного ждём, чтобы Яндекс успел сгенерировать
        time.sleep(10)
        url_check = f"https://llm.api.cloud.yandex.net/operations/{request_id}"
        headers_check = {"Authorization": f"Bearer {iam_token}"}
        response_check = requests.get(url_check, headers=headers_check)

        if (
            response_check.status_code == 200
            and "response" in response_check.json()
            and "image" in response_check.json()["response"]
        ):
            image_base64 = response_check.json()["response"]["image"]
            image_data = base64.b64decode(image_base64)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"image_{timestamp}.jpeg"
            with open(filename, "wb") as file:
                file.write(image_data)
            photo = FSInputFile(filename)
            await message.answer_photo(photo, caption=f"Вот твоя картинка по запросу:\n<code>{prompt}</code>", parse_mode=ParseMode.HTML)
            os.remove(filename)
        else:
            await message.answer("❌ Картинка пока не готова или ошибка в ответе Яндекса.")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

    await state.clear()  # Сбросить состояние

# --- Все остальные сообщения — GPT-4o-mini ---
@dp.message()
async def chat_handler(message: types.Message):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[{"role": "user", "content": message.text}],
            max_tokens=400
        )
        answer = response.choices[0].message.content
    except Exception as e:
        answer = f"⚠️ Ошибка OpenAI: {e}"
    await message.answer(answer)

# --- Запуск ---
if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
