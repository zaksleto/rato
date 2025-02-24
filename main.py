import os
import pyotp
import uvicorn
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler, CallbackContext

# Configuração do bot
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TOTP_SECRET = os.getenv("TOTP_SECRET")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))  # Seu ID para controle dos usuários

# Criando o bot e o app FastAPI
bot = Bot(token=TOKEN)
app = FastAPI()
dispatcher = Dispatcher(bot, None, workers=0, use_context=True)

# Lista de usuários permitidos
USUARIOS_PERMITIDOS = set()

# Comando /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "👋 Olá! Este bot gera códigos 2FA.\n\n"
        "Comandos disponíveis:\n"
        "🔹 /codigo - Gera um código 2FA\n"
        "🔹 /autorizar <id> - Autoriza um usuário (apenas admin)\n"
        "🔹 /remover <id> - Remove um usuário autorizado\n"
        "🔹 /limpar - Limpa a lista de usuários autorizados"
    )

# Comando /codigo
def enviar_codigo(update: Update, context: CallbackContext):
    user_id = update.message.chat_id

    if user_id not in USUARIOS_PERMITIDOS:
        update.message.reply_text("❌ Você não tem permissão para usar este comando.")
        return

    totp = pyotp.TOTP(TOTP_SECRET)
    update.message.reply_text(f"🔑 Código 2FA: `{totp.now()}`", parse_mode="Markdown")

# Comando /autorizar
def autorizar(update: Update, context: CallbackContext):
    if update.message.chat_id != OWNER_ID:
        update.message.reply_text("❌ Apenas o dono do bot pode autorizar usuários.")
        return

    try:
        user_id = int(context.args[0])
        USUARIOS_PERMITIDOS.add(user_id)
        update.message.reply_text(f"✅ Usuário {user_id} autorizado!")
    except:
        update.message.reply_text("⚠️ Uso correto: /autorizar <id>")

# Comando /remover
def remover(update: Update, context: CallbackContext):
    if update.message.chat_id != OWNER_ID:
        update.message.reply_text("❌ Apenas o dono do bot pode remover usuários.")
        return

    try:
        user_id = int(context.args[0])
        USUARIOS_PERMITIDOS.discard(user_id)
        update.message.reply_text(f"✅ Usuário {user_id} removido!")
    except:
        update.message.reply_text("⚠️ Uso correto: /remover <id>")

# Comando /limpar
def limpar(update: Update, context: CallbackContext):
    if update.message.chat_id != OWNER_ID:
        update.message.reply_text("❌ Apenas o dono do bot pode limpar a lista.")
        return

    USUARIOS_PERMITIDOS.clear()
    update.message.reply_text("✅ Lista de usuários autorizados foi limpa.")

# Adicionando handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("codigo", enviar_codigo))
dispatcher.add_handler(CommandHandler("autorizar", autorizar))
dispatcher.add_handler(CommandHandler("remover", remover))
dispatcher.add_handler(CommandHandler("limpar", limpar))

# Endpoint do Webhook para receber mensagens do Telegram
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)
    dispatcher.process_update(update)
    return {"status": "ok"}

# Endpoint para configurar o Webhook no Telegram
@app.get("/set_webhook")
async def set_webhook():
    webhook_url = f"https://{os.getenv('VERCEL_URL')}/webhook"
    bot.setWebhook(webhook_url)
    return {"message": "Webhook configurado!", "url": webhook_url"}

# Iniciar servidor local (para testes)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
