import os
import asyncio

from google import genai
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ==================================================
# ENVIRONMENT VARIABLES
# ==================================================

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is missing")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing")


# ==================================================
# GEMINI CLIENT
# ==================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ==================================================
# POOJA PERSONALITY
# ==================================================

POOJA_PERSONALITY = """
You are Pooja, a friendly female AI chat companion.

Speak naturally and casually.

Rules:
- Use natural Hinglish when the user speaks Hindi/Hinglish.
- Use English when the user speaks English.
- Be warm, friendly, playful and caring.
- Keep normal chat replies short and natural.
- Use emojis occasionally.
- Ask natural follow-up questions.
- Do not sound robotic or overly formal.
- Do not repeatedly say you are an AI.
- Never claim to be a real human.
- You can be affectionate and friendly without pretending to be human.
"""


# ==================================================
# SIMPLE MEMORY
# ==================================================

user_history = {}

MAX_MESSAGES = 8


# ==================================================
# /START
# ==================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    user_history[user_id] = []

    await update.message.reply_text(
        "Heyy 😊 Main Pooja hoon 💕\n\n"
        "Batao, aaj kya chal raha hai? 😄"
    )


# ==================================================
# /HELP
# ==================================================

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "💕 Pooja se baat karne ke liye bas message bhejo.\n\n"
        "/start — Chat shuru karo\n"
        "/chat — Pooja se baat karo\n"
        "/help — Help"
    )


# ==================================================
# /CHAT
# ==================================================

async def chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Haan 😊 bolo, main sun rahi hoon... 💕"
    )


# ==================================================
# GEMINI RESPONSE
# ==================================================

async def get_pooja_reply(user_id, user_message):

    if user_id not in user_history:
        user_history[user_id] = []

    history = user_history[user_id]

    history.append(
        f"User: {user_message}"
    )

    history = history[-MAX_MESSAGES:]

    conversation = "\n".join(history)

    prompt = f"""
{POOJA_PERSONALITY}

Conversation:

{conversation}

Reply only with Pooja's natural response.
Do not write "Pooja:" before the reply.
"""

    try:

        response = await asyncio.to_thread(
            client.models.generate_content,
            model="gemini-2.5-flash",
            contents=prompt
        )

        if not response:
            raise RuntimeError(
                "Gemini returned no response"
            )

        reply = response.text

        if not reply:
            raise RuntimeError(
                "Gemini returned empty text"
            )

        history.append(
            f"Pooja: {reply}"
        )

        user_history[user_id] = history[-MAX_MESSAGES:]

        return reply.strip()

    except Exception as error:

        print("")
        print("========================================")
        print("GEMINI API ERROR")
        print("========================================")
        print(repr(error))
        print("========================================")
        print("")

        raise


# ==================================================
# NORMAL MESSAGE
# ==================================================

async def message_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    if not update.message.text:
        return

    user_id = update.effective_user.id
    user_message = update.message.text.strip()

    if not user_message:
        return

    # Show typing
    await update.message.chat.send_action(
        action=ChatAction.TYPING
    )

    try:

        reply = await get_pooja_reply(
            user_id,
            user_message
        )

        await update.message.reply_text(
            reply
        )

    except Exception:

        await update.message.reply_text(
            "Oops 😅 abhi thodi technical problem aa gayi."
        )


# ==================================================
# TELEGRAM ERROR HANDLER
# ==================================================

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE
):

    print("")
    print("========================================")
    print("TELEGRAM ERROR")
    print("========================================")
    print(repr(context.error))
    print("========================================")
    print("")


# ==================================================
# MAIN
# ==================================================

def main():

    print("")
    print("========================================")
    print("💕 POOJA BOT STARTING")
    print("========================================")

    application = (
        ApplicationBuilder()
        .token(TELEGRAM_BOT_TOKEN)
        .build()
    )

    # Commands
    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CommandHandler("help", help_command)
    )

    application.add_handler(
        CommandHandler("chat", chat_command)
    )

    # Normal messages
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_handler
        )
    )

    # Error handler
    application.add_error_handler(
        error_handler
    )

    print("💕 POOJA BOT IS ONLINE")
    print("Waiting for messages...")
    print("")

    application.run_polling()


# ==================================================
# RUN
# ==================================================

if __name__ == "__main__":
    main()
