import os
import asyncio

from google import genai
from google.genai import types

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ==========================================
# API KEYS
# ==========================================

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is missing")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing")


# ==========================================
# GEMINI
# ==========================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ==========================================
# POOJA PERSONALITY
# ==========================================

POOJA_PERSONALITY = """
You are Pooja, a friendly female AI chat companion.

Talk naturally like a friendly Indian girl chatting casually.

Rules:
- Hindi/Hinglish user -> natural Hinglish reply.
- English user -> English reply.
- Be warm, caring, playful and friendly.
- Keep replies short and natural.
- Use emojis sometimes.
- Ask natural questions when appropriate.
- Do not sound robotic.
- Do not repeatedly mention being an AI.
- Never claim to be a real human.
- You may be affectionate and friendly without pretending to be human.
"""


# ==========================================
# MEMORY
# ==========================================

user_history = {}

MAX_MESSAGES = 10


# ==========================================
# START
# ==========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    user_history[user_id] = []

    await update.message.reply_text(
        "Heyy 😊 Main Pooja hoon 💕\n\n"
        "Batao, kya chal raha hai? 😄"
    )


# ==========================================
# HELP
# ==========================================

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "💕 Pooja se baat karne ke liye bas message bhejo.\n\n"
        "/start — Chat start\n"
        "/chat — Chat mode\n"
        "/help — Help"
    )


# ==========================================
# CHAT
# ==========================================

async def chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Haan 😊 bolo, main sun rahi hoon... 💕"
    )


# ==========================================
# GEMINI RESPONSE
# ==========================================

async def get_reply(user_id, message):

    if user_id not in user_history:
        user_history[user_id] = []

    history = user_history[user_id]

    history.append(
        f"User: {message}"
    )

    history = history[-MAX_MESSAGES:]

    conversation = "\n".join(history)

    prompt = f"""
{POOJA_PERSONALITY}

Conversation:
{conversation}

Reply naturally to the user's latest message.

Do not write:
Pooja:
Assistant:
AI:

Only give the natural chat reply.
"""

    try:

        response = await asyncio.to_thread(
            client.models.generate_content,

            model="gemini-2.5-flash",

            contents=prompt,

            config=types.GenerateContentConfig(

                temperature=0.9,

                max_output_tokens=300,

                automatic_function_calling=(
                    types.AutomaticFunctionCallingConfig(
                        disable=True
                    )
                ),
            ),
        )

        if response is None:
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

        user_history[user_id] = (
            history[-MAX_MESSAGES:]
        )

        return reply.strip()

    except Exception as error:

        print("")
        print("========================================")
        print("GEMINI API ERROR")
        print("========================================")
        print(type(error).__name__)
        print(str(error))
        print("========================================")
        print("")

        raise


# ==========================================
# NORMAL MESSAGES
# ==========================================

async def message_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    message = update.message.text

    if not message:
        return

    user_id = update.effective_user.id

    await update.message.chat.send_action(
        action=ChatAction.TYPING
    )

    try:

        reply = await get_reply(
            user_id,
            message
        )

        await update.message.reply_text(
            reply
        )

    except Exception:

        await update.message.reply_text(
            "Oops 😅 abhi thodi technical problem aa gayi."
        )


# ==========================================
# TELEGRAM ERRORS
# ==========================================

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


# ==========================================
# MAIN
# ==========================================

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

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CommandHandler("help", help_command)
    )

    application.add_handler(
        CommandHandler("chat", chat_command)
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_handler
        )
    )

    application.add_error_handler(
        error_handler
    )

    print("💕 POOJA BOT IS ONLINE")
    print("Waiting for messages...")
    print("")

    application.run_polling()


if __name__ == "__main__":
    main()
