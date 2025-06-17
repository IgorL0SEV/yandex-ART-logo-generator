# Telegram AI Assistant + Image Generator

**Умный Telegram-бот на Python**  
- Общается на любые темы через OpenAI (`gpt-4o-mini`)
- Генерирует изображения по описанию с помощью Яндекс Art API
- Минимализм, простота доработки, поддержка `.env`


## 🚀 Быстрый старт

### 1. Клонируй репозиторий
git clone https://github.com/yourusername/your-bot-repo.git
cd your-bot-repo
2. Создай виртуальное окружение
python -m venv venv
source venv/bin/activate     # Linux/macOS
venv\Scripts\activate        # Windows
3. Установи зависимости
pip install -r requirements.txt
4. Создай файл .env в корне проекта
env
BOT_TOKEN=твой_токен_бота_от_BotFather
OPENAI_API_KEY=sk-...         # API-ключ OpenAI
OAUTH_TOKEN=...               # OAuth-токен Yandex.Cloud (долгоживущий)
CATALOG_ID=...                # ID каталога Яндекс Cloud

Внимание:
Кавычки не нужны!

Все ключи должны быть валидными.

Подробнее про получение токенов смотри инструкцию ниже.

5. Запусти бота
python main.py
✨ Возможности
/start — приветствие
/image — запрос описания картинки, генерация изображения через Яндекс.Art и отправка прямо в чат

Любые другие сообщения — ответы через OpenAI (gpt-4o-mini)

🔑 Ключи и токены
Telegram Bot Token
Получи у @BotFather

Пример: 1234567890:AAE7Sy5U-abcdefghijklmnopqrstuvwxyzABC

OpenAI API Key
Получи на https://platform.openai.com/api-keys

Пример: sk-abc123...

Yandex OAuth Token - долгоживущий OAuth-токен, а не IAM Token!

Catalog ID (Яндекс) - найди в панели управления Yandex Cloud или через CLI
Обычно выглядит как: b1ggjq8s4h8k56dhta85

⚙️ Зависимости
aiogram>=3.0
openai>=1.0
python-dotenv
requests

Инфо в requirements.txt

🛠 Настройки и кастомизация
Промпты, сообщения, модель OpenAI можно менять в коде.
Интервал ожидания для Яндекс.Art (time.sleep(10)) при необходимости увеличить/уменьшить.
Все функции обернуты обработчиками ошибок для устойчивости работы.

📝 Пример использования
Напиши /start — бот ответит приветствием.
Напиши любое сообщение — получишь AI-ответ.
Введи /image — бот попросит текстовое описание картинки.
Введи описание (например: Сказочный замок на закате, в облаках, стиль арт-деко) — получишь уникальное изображение в ответ.

🚨 Важно
Все токены и ключи держи в секрете!
Для работы с OpenAI и Яндекс Cloud могут быть затраты на использование API.
.env не включай в публичный git-репозиторий!

