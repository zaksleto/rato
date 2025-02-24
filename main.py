import os
import pyotp
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Configurações
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TOTP_SECRET = os.environ.get("TOTP_SECRET")

# Defina seu ID de administrador (seu próprio ID do Telegram)
ADMIN_ID = 510738503  # 🔴 Substitua pelo seu ID real!

# Arquivo onde serão salvos os usuários permitidos
USUARIOS_FILE = "usuarios_permitidos.txt"


# Função para carregar usuários permitidos do arquivo
def carregar_usuarios():
    try:
        with open(USUARIOS_FILE, "r") as f:
            return [int(line.strip()) for line in f.readlines()]
    except FileNotFoundError:
        return []


# Função para salvar usuários no arquivo
def salvar_usuarios():
    with open(USUARIOS_FILE, "w") as f:
        for user_id in USUARIOS_PERMITIDOS:
            f.write(f"{user_id}\n")


# Carrega usuários permitidos do arquivo
USUARIOS_PERMITIDOS = carregar_usuarios()


def start(update: Update, context: CallbackContext):
    """ Responde ao comando /start """
    user_id = update.message.chat_id
    update.message.reply_text(
        f"👋 Olá! Seu ID é `{user_id}`.\n\n"
        "Use `/codigo` para gerar um código 2FA (se permitido).\n"
        "Admin pode usar:\n"
        "🔹 `/autorizar ID_DO_USUARIO`\n"
        "🔹 `/remover ID_DO_USUARIO`\n"
        "🔹 `/limpar` (remove todos os usuários)",
        parse_mode="Markdown")


def enviar_codigo(update: Update, context: CallbackContext):
    """ Envia o código 2FA apenas para usuários autorizados """
    user_id = update.message.chat_id

    if user_id not in USUARIOS_PERMITIDOS:
        update.message.reply_text(
            "❌ Você não tem permissão para usar este comando.")
        return

    if not TOTP_SECRET:
        update.message.reply_text("⚠️ Erro: chave 2FA não configurada.")
        return

    totp = pyotp.TOTP(TOTP_SECRET)
    codigo = totp.now()
    update.message.reply_text(f"🔑 Código 2FA: `{codigo}`",
                              parse_mode="Markdown")


def autorizar_usuario(update: Update, context: CallbackContext):
    """ Permite que o ADMIN adicione novos usuários à lista """
    user_id = update.message.chat_id

    if user_id != ADMIN_ID:
        update.message.reply_text(
            "🚫 Você não tem permissão para usar este comando.")
        return

    try:
        novo_user_id = int(context.args[0])
    except (IndexError, ValueError):
        update.message.reply_text("❌ Use: `/autorizar ID_DO_USUARIO`")
        return

    if novo_user_id in USUARIOS_PERMITIDOS:
        update.message.reply_text("✅ Esse usuário já está autorizado.")
    else:
        USUARIOS_PERMITIDOS.append(novo_user_id)
        salvar_usuarios()
        update.message.reply_text(
            f"✅ Usuário `{novo_user_id}` autorizado com sucesso!",
            parse_mode="Markdown")


def remover_usuario(update: Update, context: CallbackContext):
    """ Remove um usuário da lista de autorizados """
    user_id = update.message.chat_id

    if user_id != ADMIN_ID:
        update.message.reply_text(
            "🚫 Você não tem permissão para usar este comando.")
        return

    try:
        remover_user_id = int(context.args[0])
    except (IndexError, ValueError):
        update.message.reply_text("❌ Use: `/remover ID_DO_USUARIO`")
        return

    if remover_user_id in USUARIOS_PERMITIDOS:
        USUARIOS_PERMITIDOS.remove(remover_user_id)
        salvar_usuarios()
        update.message.reply_text(
            f"✅ Usuário `{remover_user_id}` removido com sucesso!",
            parse_mode="Markdown")
    else:
        update.message.reply_text("⚠️ Esse usuário não está autorizado.")


def limpar_lista(update: Update, context: CallbackContext):
    """ Remove todos os usuários da lista """
    user_id = update.message.chat_id

    if user_id != ADMIN_ID:
        update.message.reply_text(
            "🚫 Você não tem permissão para usar este comando.")
        return

    USUARIOS_PERMITIDOS.clear()
    salvar_usuarios()
    update.message.reply_text("⚠️ Lista de usuários **limpa com sucesso**!",
                              parse_mode="Markdown")


def main():
    if not TOKEN:
        print("Erro: token do bot não configurado.")
        return

    updater = Updater(TOKEN)
    dp = updater.dispatcher

    # Adiciona comandos ao bot
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("codigo", enviar_codigo))
    dp.add_handler(CommandHandler("autorizar", autorizar_usuario))
    dp.add_handler(CommandHandler("remover", remover_usuario))  # Novo comando
    dp.add_handler(CommandHandler("limpar", limpar_lista))  # Novo comando

    # Inicia o bot
    updater.start_polling()
    print("✅ Bot rodando! Pressione Ctrl+C para parar.")
    updater.idle()


if __name__ == '__main__':
    main()
