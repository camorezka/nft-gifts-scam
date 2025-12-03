# server.py
from quart import Quart, request, jsonify
from telethon import TelegramClient
from telethon.errors.rpcerrorlist import PhoneNumberUnoccupiedError

api_id = 20364764  # твой api_id
api_hash = "fdbe60e03331c8ac7cf3ddca2404feaa"

client = TelegramClient("session_name", api_id, api_hash)
app = Quart(__name__)

@app.post("/send_code")
async def send_code():
    data = await request.get_json()
    phone = data["phone"]

    await client.connect()
    try:
        await client.send_code_request(phone)
        return jsonify({"status": "ok"})
    except PhoneNumberUnoccupiedError:
        return jsonify({"status": "error", "msg": "Номер не связан с Telegram"})

@app.post("/check_code")
async def check_code():
    data = await request.get_json()
    phone = data["phone"]
    code = data["code"]

    try:
        await client.sign_in(phone, code)
        return jsonify({"status": "success"})
    except Exception:
        return jsonify({"status": "error", "msg": "Неверный код"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
