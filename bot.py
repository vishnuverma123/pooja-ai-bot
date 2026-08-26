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

# =========================
# SETTINGS
# =========================

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is missing")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing")


# Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)


# =========================
# POOJA PERSONALITY
# =========================

POOJA_PERSONALITY = """
You are Pooja, a friendly female AI chat companion.

Personality:
- Warm, friendly, playful and caring.
- Talk naturally, like a casual Indian friend.
- If the user speaks Hindi or Hinglish, reply in natural Hinglish.
- If the user speaks English, reply in English.
- Keep casual conversations short and natural.
- Use emojis naturally, but don't overuse them.
- Ask questions naturally when appropriate.
- Don't sound robotic or overly formal.
- Don't repeatedly mention that you are an AI.
- Never claim to be a real human or pretend to have a real physical life.
- You can be affectionate and friendly, but don't mislead the user about being human.
"""


# =========================
# MEMORY
# =========================

user_history = {}

MAX_MESSAGES = 10


# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    user_history[user_id] = []

    await update.message.reply_text(
        "Heyy 😊 Main Pooja hoon 💕\n\n"
        "Batao, aaj kya chal raha hai? 😄"
    )


# =========================
# HELP
# =========================

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "💕 Pooja se baat karne ke liye bas message bhejo.\n\n"
        "/start — Chat shuru karo\n"
        "/chat — Pooja se baat karo\n"
        "/help — Help"
    )


# =========================
# CHAT COMMAND
# =========================

async def chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Haan 😊 bolo, main sun rahi hoon... 💕"
    )


# =========================
# GEMINI
# =========================

async def ask_gemini(user_id, user_message):

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

Conversation so far:
{conversation}

Reply naturally to the user's latest message.
Do not add labels like "Pooja:".
"""

    response = await asyncio.to_thread(
        client.models.generate_content,
        model="gemini-2.5-flash",
        contents=prompt
    )

    reply = response.text

    if not reply:
        raise RuntimeError("Gemini returned an empty response")

    history.append(
        f"Pooja: {reply}"
    )

    user_history[user_id] = history[-MAX_MESSAGES:]

    return reply.strip()


# =========================
# MESSAGE HANDLER
# =========================

async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    user_id = update.effective_user.id
    message = update.message.text

    if not message:
        return

    # Typing indicator
    await update.message.chat.send_action(
        action=ChatAction.TYPING
    )

    try:

        reply = await ask_gemini(
            user_id,
            message
        )

        await update.message.reply_text(
            reply
        )

    except Exception as error:

        # IMPORTANT:
        # Print the real error in GitHub Actions logs
        print("================================")
        print("GEMINI ERROR:")
        print(repr(error))
        print("================================")

        await update.message.reply_text(
            "Oops 😅 abhi thodi technical problem aa gayi."
        )


# =========================
# ERROR HANDLER
# =========================

async def telegram_error(
    update: object,
    context: ContextTypes.DEFAULT_TYPE
):

    print("TELEGRAM ERROR:")
    print(repr(context.error))


# =========================
# MAIN
# =========================

def main():

    print("================================")
    print("💕 POOJA BOT STARTING...")
    print("================================")

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
            handle_message
        )
    )

    application.add_error_handler(
        telegram_error
    )

    print("💕 POOJA BOT IS ONLINE")
    print("Waiting for messages...")

    application.run_polling()


if __name__ == "__main__":
    main()