import os
import requests
import random
import time
import datetime
import base64
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

OAUTH_TOKEN = os.getenv("OAUTH_TOKEN")
CATALOG_ID = os.getenv("CATALOG_ID")
# IAM_TOKEN = os.getenv("IAM_TOKEN")
client = openai.OpenAI(api_key="sk-...")


def get_iam_token(oauth_token):
    url = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
    response = requests.post(
        url,
        json={"yandexPassportOauthToken": oauth_token}
    )
    if response.status_code == 200:
        return response.json()["iamToken"]
    else:
        raise Exception(f"Ошибка при получении IAM_TOKEN: {response.status_code} {response.text}")

# Получаем актуальный IAM_TOKEN перед каждым запуском
IAM_TOKEN = get_iam_token(OAUTH_TOKEN)
print(f"IAM_TOKEN: {IAM_TOKEN[:10]}...")  # для проверки (только начало, чтобы не светить весь)



ABC = "узор из цветных пастельных суккулентов разных сортов, hd full wallpaper, четкий фокус, множество сложных деталей, глубина кадра, вид сверху"
A1 = "футуристический город ночью, сияющие неоновые вывески, отражения на мокром асфальте, огромные небоскрёбы, киберпанк стиль, много деталей, вид сверху"
A2 = "ярко-красный ретро-кабриолет на побережье, стиль 1960-х, голубое небо, мягкое солнечное освещение, детализация, атмосфера свободы"
A3 = "волшебный лес на рассвете, туман между деревьями, лучи света, мох, большие старые деревья, сказочная атмосфера, спокойствие"
A4 = "абстрактная минималистичная композиция, геометрические формы, пастельные цвета, белый фон, чистый современный стиль"
A5 = "портрет совы в стиле акварели, крупный план, мягкие цвета, выразительные глаза, художественный фон"
A6 = "фэнтези-замок на вершине скалы, облака внизу, розовое небо, дракон летит вдалеке, много света и тени, эпическая сцена"
A7 = "паровоз, едущий по рельсам сквозь порталы времени, пейзаж меняется от древних времён до футуризма, динамика, спецэффекты"
A8 = "робот-исследователь на поверхности неизвестной планеты, звёзды на фоне, загадочные структуры, научно-фантастическая атмосфера"


# 1. Загружаем переменные из .env
load_dotenv()

IAM_TOKEN = os.getenv("IAM_TOKEN")
CATALOG_ID = os.getenv("CATALOG_ID")

if not IAM_TOKEN or not CATALOG_ID:
    raise ValueError("Ошибка: Не найден IAM_TOKEN или CATALOG_ID в .env!")

# 2. Готовим запрос для генерации изображения
url = "https://llm.api.cloud.yandex.net/foundationModels/v1/imageGenerationAsync"

headers = {
    "Authorization": f"Bearer {IAM_TOKEN}",
    "Content-Type": "application/json"
}

data = {
    "modelUri": f"art://{CATALOG_ID}/yandex-art/latest",
    "generationOptions": {
        "seed": str(random.randint(0, 1000000)),
        # seed - зерно генерации, любое число от 0 до (2 [в степени 63] минус 1)
        # при одном и том же промте и зерне генерации результат генерации будет одинаковым
        "aspectRatio": {
            "widthRatio": "2",
            "heightRatio": "1"
        }
    },
    "messages": [
        {
            "weight": "1",
            # "text" : " ОПИСАНИЕ ПРОМПТА "
            "text": A3
        }
    ]
}

# 3. Отправляем запрос на генерацию
response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    request_id = response.json().get('id')
    print(f"🟢 Запрос отправлен. ID: {request_id}")

    # 4. Ждем, затем запрашиваем результат
    time.sleep(10)  # Можно увеличить, если часто не успевает

    # Headers для второго запроса (Content-Type не нужен)
    headers_check = {
        "Authorization": f"Bearer {IAM_TOKEN}"
    }

    url_check = f"https://llm.api.cloud.yandex.net/operations/{request_id}"
    response_check = requests.get(url_check, headers=headers_check)

    if response_check.status_code == 200:
        resp_json = response_check.json()
        print(resp_json)
        # Проверяем, есть ли изображение в ответе
        try:
            image_base64 = resp_json['response']['image']
            image_data = base64.b64decode(image_base64)
            # Генерируем уникальное имя файла с датой и временем
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"image_{timestamp}.jpeg"

            with open(filename, 'wb') as file:
                file.write(image_data)
            print(f"✅ Изображение успешно сохранено как {filename}")
        except (KeyError, TypeError):
            print("⚠️ Изображение ещё не готово или формат ответа изменился.")
            print(resp_json)
    else:
        print(f"Ошибка: {response_check.status_code} - {response_check.text}")
else:
    print(f"Ошибка при запросе генерации: {response.status_code} - {response.text}")
