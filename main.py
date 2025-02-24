import os
import pyotp
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Buscando as variáveis de ambiente
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TOTP_SECRET = os.environ.get("TOTP_SECRET")

def enviar_codigo(update: Update, context: CallbackContext):
    if not TOTP_SECRET:
        update.message.reply_text("Erro: chave secreta 2FA não configurada.")
        return

    totp = pyotp.TOTP(TOTP_SECRET)
    codigo = totp.now()
    update.message.reply_text(f"Código 2FA: {codigo}")

def main():
    if not TOKEN:
        print("Erro: token do bot não configurado.")
        return

    updater = Updater(TOKEN)
    dp = updater.dispatcher

    # Adiciona o comando /codigo
    dp.add_handler(CommandHandler("codigo", enviar_codigo))

    updater.start_polling()
    print("Bot rodando. Pressione Ctrl+C para parar.")
    updater.idle()

if __name__ == '__main__':
    main()
